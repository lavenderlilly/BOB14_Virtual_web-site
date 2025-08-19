from flask import Flask, request, jsonify, session, redirect, url_for, render_template
import hashlib
import uuid
import time
import hmac
import base64
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# 세션 저장소 (Redis로 교체 가능하도록 추상화)
class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.expiry_times: Dict[str, float] = {}
    
    def set(self, key: str, value: Dict, expiry_seconds: int = 600):
        self.sessions[key] = value
        self.expiry_times[key] = time.time() + expiry_seconds
    
    def get(self, key: str) -> Optional[Dict]:
        if key not in self.sessions:
            return None
        
        if time.time() > self.expiry_times.get(key, 0):
            self.delete(key)
            return None
        
        return self.sessions[key]
    
    def delete(self, key: str):
        if key in self.sessions:
            del self.sessions[key]
        if key in self.expiry_times:
            del self.expiry_times[key]

# 전역 세션 저장소
session_store = SessionStore()

# JWT 토큰 관리
class JWTHandler:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode('utf-8')
    
    def create_jwt(self, payload: Dict, expiry_seconds: int = 600) -> str:
        header = {
            "alg": "HS256",
            "typ": "JWT"
        }
        
        payload.update({
            "iat": int(time.time()),
            "exp": int(time.time()) + expiry_seconds,
            "jti": str(uuid.uuid4())  # 재사용 방지
        })
        
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
        
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(self.secret_key, message.encode(), hashlib.sha256).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
        
        return f"{message}.{signature_b64}"
    
    def verify_jwt(self, token: str) -> Optional[Dict]:
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header_b64, payload_b64, signature_b64 = parts
            
            # 서명 검증
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(self.secret_key, message.encode(), hashlib.sha256).digest()
            expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).rstrip(b'=').decode()
            
            if not hmac.compare_digest(signature_b64, expected_signature_b64):
                return None
            
            # 페이로드 디코딩
            payload = json.loads(base64.urlsafe_b64decode(payload_b64 + '===').decode())
            
            # 만료시간 검증
            if time.time() > payload.get('exp', 0):
                return None
            
            return payload
        except:
            return None

jwt_handler = JWTHandler(app.secret_key)

# 사용된 JTI 추적 (재사용 방지)
used_jtis = set()

# 실명확인 서비스 (Mock)
def verify_realname(name: str, rrn: str) -> bool:
    # 실제로는 공공데이터포털 API 호출
    # 여기서는 간단한 검증만 수행
    if not name or not rrn:
        return False
    
    # 주민번호 형식 검증 (간단한 예시)
    if len(rrn) != 14 or rrn[6] != '-':
        return False
    
    return True

# 외부 인증기관 Mock (PASS/카카오/네이버 등)
class ExternalIdP:
    def __init__(self):
        self.idp_secret = "idp-secret-key-change-this"
    
    def create_auth_url(self, request_id: str, state: str) -> str:
        # 실제로는 각 인증기관의 OAuth URL
        return f"/mock_idp_auth?request_id={request_id}&state={state}"
    
    def verify_token(self, idp_signed_token: str) -> Optional[Dict]:
        try:
            # Mock 토큰 검증 (실제로는 각 인증기관의 공개키로 검증)
            payload = jwt_handler.verify_jwt(idp_signed_token)
            if not payload:
                return None
            
            # JTI 재사용 방지
            jti = payload.get('jti')
            if jti in used_jtis:
                return None
            used_jtis.add(jti)
            
            return payload
        except:
            return None

idp = ExternalIdP()

# 유틸리티 함수
def generate_subject_hash(name: str, rrn: str) -> str:
    """사용자 식별을 위한 해시 생성"""
    data = f"{name}:{rrn}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def generate_secure_random() -> str:
    """암호학적으로 안전한 랜덤값 생성"""
    return secrets.token_urlsafe(32)

# 1단계: 실명확인
@app.route("/step1/realname", methods=["POST"])
def step1_realname():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        name = data.get("name", "").strip()
        rrn = data.get("rrn", "").strip()
        
        # 입력값 검증
        if not name or not rrn:
            return jsonify({"error": "Missing required fields"}), 400
        
        # 실명확인 수행
        if not verify_realname(name, rrn):
            return jsonify({"error": "Real name verification failed"}), 400
        
        # 주민등록번호 형식 통일 (뒷자리 첫 번째 숫자만 사용, 나머지는 0으로 채움)
        rrn_parts = rrn.split('-')
        if len(rrn_parts) == 2:
            rrn_front = rrn_parts[0]
            rrn_back = rrn_parts[1]
            if len(rrn_back) >= 1:
                rrn_back_first = rrn_back[0]
                rrn_normalized = f"{rrn_front}-{rrn_back_first}000000"
            else:
                rrn_normalized = rrn
        else:
            rrn_normalized = rrn
        
        # 세션 ID 생성
        sid = str(uuid.uuid4())
        
        # 사용자 해시값 생성 및 저장 (정규화된 주민등록번호 사용)
        subject_hash = generate_subject_hash(name, rrn_normalized)
        
        # state, nonce 생성
        state = generate_secure_random()
        nonce = generate_secure_random()
        
        # 세션에 저장 (개인정보는 서버 내부에서만 처리)
        session_data = {
            "step": "step1_completed",
            "subject_hash": subject_hash,
            "user_name": name,
            "user_rrn": rrn,
            "state": state,
            "nonce": nonce,
            "created_at": time.time()
        }
        
        session_store.set(sid, session_data, expiry_seconds=600)  # 10분 만료
        
        print(f"✅ 1단계 실명확인 성공: {name} (SID: {sid})")
        print(f"🔐 Subject Hash: {subject_hash}")
        
        # 클라이언트에는 sid만 반환 (개인정보 절대 노출 금지)
        return jsonify({"sid": sid}), 200
        
    except Exception as e:
        print(f"❌ 1단계 실명확인 오류: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 2단계: 외부 인증 초기화 (보안 강화)
@app.route("/step2/init", methods=["POST"])
def step2_init():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        sid = data.get("sid", "").strip()
        
        # 세션 확인
        session_data = session_store.get(sid)
        if not session_data or session_data.get("step") != "step1_completed":
            return jsonify({"error": "Invalid session or step"}), 400
        
        # 1단계 사용자 정보 (서버에 저장된 정보만 사용)
        step1_name = session_data.get("user_name")
        step1_rrn = session_data.get("user_rrn")
        
        print(f"🔍 1단계 사용자: {step1_name}, {step1_rrn}")
        
        # request_id 생성
        request_id = str(uuid.uuid4())
        
        # 세션 업데이트 (1단계 사용자 정보 유지)
        session_data["request_id"] = request_id
        session_data["step"] = "step2_initiated"
        session_store.set(sid, session_data, expiry_seconds=600)
        
        # 인증기관 URL 생성 (1단계 사용자 정보로 요청)
        auth_url = idp.create_auth_url(request_id, session_data["state"])
        
        print(f"🔄 2단계 인증 초기화: SID {sid}, Request ID {request_id}")
        print(f"✅ 보안: 1단계 사용자 정보({step1_name})로 IDP 요청")
        
        return jsonify({
            "auth_url": auth_url,
            "request_id": request_id,
            "nonce": session_data["nonce"]
        }), 200
        
    except Exception as e:
        print(f"❌ 2단계 초기화 오류: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 2단계: 외부 인증 콜백
@app.route("/step2/callback", methods=["POST"])
def step2_callback():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        request_id = data.get("request_id", "").strip()
        state = data.get("state", "").strip()
        idp_signed_token = data.get("idp_signed_token", "").strip()
        
        # 필수 파라미터 검증
        if not request_id or not state or not idp_signed_token:
            return jsonify({"error": "Missing required parameters"}), 400
        
        # request_id로 세션 찾기
        session_data = None
        sid = None
        for session_id, data in session_store.sessions.items():
            if data.get("request_id") == request_id:
                session_data = data
                sid = session_id
                break
        
        if not session_data or session_data.get("step") != "step2_initiated":
            return jsonify({"error": "Invalid session or step"}), 400
        
        # 1. State 검증
        if not hmac.compare_digest(state, session_data.get("state", "")):
            print(f"❌ State 불일치: {state} != {session_data.get('state')}")
            return jsonify({"error": "Invalid state"}), 400
        
        # 2. IDP 토큰 검증
        idp_payload = idp.verify_token(idp_signed_token)
        if not idp_payload:
            print("❌ IDP 토큰 검증 실패")
            return jsonify({"error": "Invalid IDP token"}), 400
        
        # 3. Nonce 검증
        if not hmac.compare_digest(idp_payload.get("nonce", ""), session_data.get("nonce", "")):
            print(f"❌ Nonce 불일치: {idp_payload.get('nonce')} != {session_data.get('nonce')}")
            return jsonify({"error": "Invalid nonce"}), 400
        print("✅ Nonce 검증 성공")
        
        # 4. 사용자 정보 추출 및 해시 계산
        idp_name = idp_payload.get("name", "")
        idp_rrn = idp_payload.get("rrn", "")
        subject_hash_idp = generate_subject_hash(idp_name, idp_rrn)
        
        # 5. 1단계와 2단계 사용자 일치성 검증 (보안 강화)
        subject_hash_step1 = session_data.get("subject_hash", "")
        
        print(f"📋 1단계 사용자: {session_data.get('user_name')}, {session_data.get('user_rrn')}")
        print(f"📋 2단계 사용자: {idp_name}, {idp_rrn}")
        print(f"📋 1단계 Subject Hash: {subject_hash_step1}")
        print(f"📋 2단계 Subject Hash: {subject_hash_idp}")
        
        # 사용자 일치성 검증 (취약점 시뮬레이션용 - 주석 처리)
        # if not hmac.compare_digest(subject_hash_step1, subject_hash_idp):
        #     print("❌ 사용자 일치성 검증 실패!")
        #     print(f"🚨 1단계: {session_data.get('user_name')} → 2단계: {idp_name}")
        #     print(f"🚨 1단계와 2단계 인증자가 다릅니다. 본인인증이 실패했습니다.")
        #     return jsonify({
        #         "error": "USER_MISMATCH",
        #         "message": "1단계와 2단계 인증자가 일치하지 않습니다. 본인인증이 실패했습니다."
        #     }), 400
        
        # 취약점 시뮬레이션: 사용자 일치성 검증을 하지 않음
        print("⚠️ 취약점 시뮬레이션: 사용자 일치성 검증을 하지 않음!")
        print(f"🚨 1단계: {session_data.get('user_name')} → 2단계: {idp_name}")
        print(f"🚨 파라미터 변조 취약점으로 인해 다른 사용자로 인증 성공")
        
        print("✅ 사용자 일치성 검증 성공")
        
        # 6. 세션 업데이트 (1단계 사용자 정보 유지)
        session_data["step"] = "step2_ok"
        # 2단계 인증은 성공했지만, 최종 개통은 1단계 사용자 명의로 진행
        session_data["final_user"] = {
            "name": session_data.get("user_name"),  # 1단계 사용자
            "rrn": session_data.get("user_rrn"),    # 1단계 사용자
            "subject_hash": session_data.get("subject_hash")  # 1단계 사용자
        }
        session_data["idp_user"] = {
            "name": idp_name,
            "rrn": idp_rrn,
            "subject_hash": subject_hash_idp
        }
        session_store.set(sid, session_data, expiry_seconds=600)
        
        print(f"✅ 2단계 인증 성공: {idp_name}")
        print(f"🎯 최종 개통 예정: {session_data.get('user_name')} (1단계 사용자)")
        
        return jsonify({
            "success": True,
            "sid": sid
        }), 200
        
    except Exception as e:
        print(f"❌ 2단계 콜백 오류: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 최종 완료
@app.route("/finalize", methods=["POST"])
def finalize():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        sid = data.get("sid", "").strip()
        
        # 세션 확인
        session_data = session_store.get(sid)
        if not session_data or session_data.get("step") != "step2_ok":
            return jsonify({"error": "Invalid session or incomplete steps"}), 400
        
        # 최종 JWT 발급 (1단계 사용자 명의로)
        final_user = session_data.get("final_user", {})
        final_payload = {
            "sid": sid,
            "user_verified": True,
            "auth_level": "2fa_completed",
            "final_user_name": final_user.get("name"),
            "final_user_rrn": final_user.get("rrn")
        }
        
        final_jwt = jwt_handler.create_jwt(final_payload, expiry_seconds=3600)  # 1시간
        
        # 세션 정리
        session_store.delete(sid)
        
        print(f"🎉 최종 인증 완료: SID {sid}")
        print(f"📱 개통 완료: {final_user.get('name')} 명의")
        
        # IDP 사용자 정보 확인 (파라미터 변조 시뮬레이션용)
        idp_user = session_data.get("idp_user", {})
        data_mismatch = final_user.get("name") != idp_user.get("name")
        
        # 세션에 개통 완료 정보 저장
        session["contract_complete"] = {
            "step1_data": {
                "name": final_user.get("name"),
                "resident_number": final_user.get("rrn"),
                "phone": "010-1234-5678"
            },
            "step2_data": {
                "name": idp_user.get("name", final_user.get("name")),  # IDP 사용자 또는 동일 사용자
                "phone": "010-9876-5432",
                "provider": "PASS"
            },
            "data_mismatch": data_mismatch
        }
        
        return jsonify({
            "success": True,
            "jwt": final_jwt,
            "message": f"{final_user.get('name')} 명의로 2단계 인증이 성공적으로 완료되었습니다.",
            "redirect_url": "/contract_complete"
        }), 200
        
    except Exception as e:
        print(f"❌ 최종 완료 오류: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 테스트용 Mock IDP 인증 페이지
@app.route("/mock_idp_auth")
def mock_idp_auth():
    request_id = request.args.get("request_id")
    state = request.args.get("state")
    
    if not request_id or not state:
        return "Invalid parameters", 400
    
    return render_template("mock_idp_auth.html", request_id=request_id, state=state)

# 1단계 실명확인 페이지
@app.route("/step1_verification", methods=["GET", "POST"])
def step1_verification():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON"}), 400
            
            name = data.get("name", "").strip()
            resident_number = data.get("resident_number", "").strip()
            phone = data.get("phone", "").strip()
            
            # 간단한 검증 (실제로는 더 복잡한 검증 필요)
            if name and resident_number and phone:
                # 세션에 1단계 정보 저장
                session["step1_data"] = {
                    "name": name,
                    "resident_number": resident_number,
                    "phone": phone,
                    "completed": True
                }
                return jsonify({"success": True}), 200
            else:
                return jsonify({"error": "모든 필드를 입력해주세요."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template("step1_verification.html")

# 2단계 본인인증 페이지
@app.route("/step2_verification", methods=["GET", "POST"])
def step2_verification():
    # 1단계 완료 확인
    if not session.get("step1_data", {}).get("completed"):
        return redirect(url_for("step1_verification"))
    
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON"}), 400
            
            provider = data.get("provider", "").strip()
            
            if provider:
                # 2단계 인증 시뮬레이션 (실제로는 외부 인증 기관 연동)
                session["step2_data"] = {
                    "name": "이영희",  # 2단계에서 다른 사용자로 인증
                    "phone": "010-9876-5432",
                    "provider": provider,
                    "completed": True
                }
                
                return jsonify({"success": True}), 200
            else:
                return jsonify({"error": "인증 기관을 선택해주세요."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # 인증 기관 목록
    providers = {
        "pass": {
            "name": "PASS",
            "logo": "P",
            "color": "bg-red-500",
            "description": "공동인증서 기반 간편인증"
        },
        "kakao": {
            "name": "카카오",
            "logo": "K",
            "color": "bg-yellow-500",
            "description": "카카오톡 간편인증"
        },
        "naver": {
            "name": "네이버",
            "logo": "N",
            "color": "bg-green-500",
            "description": "네이버 간편인증"
        }
    }
    
    return render_template("step2_verification.html", providers=providers)

# 개통 완료 페이지
@app.route("/contract_complete")
def contract_complete():
    print("🔍 contract_complete 라우트 호출됨")
    
    # step1_verification에서 온 경우
    step1_data = session.get("step1_data", {})
    step2_data = session.get("step2_data", {})
    
    print(f"📋 step1_data: {step1_data}")
    print(f"📋 step2_data: {step2_data}")
    
    # secure_auth에서 온 경우
    contract_complete_data = session.get("contract_complete", {})
    print(f"📋 contract_complete_data: {contract_complete_data}")
    
    if contract_complete_data:
        # secure_auth 시스템에서 온 경우
        print("🔍 secure_auth 시스템에서 온 경우")
        step1_data = contract_complete_data.get("step1_data", {})
        step2_data = contract_complete_data.get("step2_data", {})
        data_mismatch = contract_complete_data.get("data_mismatch", False)
        
        # 세션 정리
        session.pop("contract_complete", None)
    elif step1_data.get("completed") and step2_data.get("completed"):
        # step1_verification 시스템에서 온 경우
        print("🔍 step1_verification 시스템에서 온 경우")
        data_mismatch = step1_data.get("name") != step2_data.get("name")
        print(f"🔍 data_mismatch: {data_mismatch}")
        
        # 세션 정리
        session.pop("step1_data", None)
        session.pop("step2_data", None)
    else:
        print("❌ 세션 데이터가 없어서 index로 리다이렉트")
        return redirect(url_for("index"))
    
    # 인증 기관 정보
    provider_info = {
        "pass": {"name": "PASS"},
        "kakao": {"name": "카카오"},
        "naver": {"name": "네이버"}
    }.get(step2_data.get("provider"), {"name": "알 수 없음"})
    
    return render_template("contract_complete.html", 
                         step1_data=step1_data,
                         step2_data=step2_data,
                         provider_info=provider_info,
                         data_mismatch=data_mismatch)

# Mock IDP 토큰 생성 (테스트용)
@app.route("/mock_idp_token", methods=["POST"])
def mock_idp_token():
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        rrn = data.get("rrn", "").strip()
        nonce = data.get("nonce", "").strip()
        request_id = data.get("request_id", "").strip()
        state = data.get("state", "").strip()
        
        if not name or not rrn or not nonce or not request_id or not state:
            return jsonify({"error": "Missing required fields"}), 400
        
        # 세션에서 1단계 사용자 정보 가져오기
        session_data = None
        for sid, session in session_store.sessions.items():
            if session.get("request_id") == request_id and session.get("state") == state:
                session_data = session
                break
        
        if not session_data:
            return jsonify({"error": "Invalid session"}), 400
        
        # 1단계 사용자 정보
        step1_name = session_data.get("user_name")
        step1_rrn = session_data.get("user_rrn")
        step1_subject_hash = session_data.get("subject_hash")
        
        # 2단계 사용자 해시 계산
        step2_subject_hash = generate_subject_hash(name, rrn)
        
        print(f"🔍 1단계 사용자: {step1_name}, {step1_rrn}")
        print(f"🔍 2단계 사용자: {name}, {rrn}")
        print(f"🔍 1단계 해시: {step1_subject_hash}")
        print(f"🔍 2단계 해시: {step2_subject_hash}")
        
        # 사용자 일치성 검증 (보안 강화)
        if not hmac.compare_digest(step2_subject_hash, step1_subject_hash):
            print("❌ 사용자 일치성 검증 실패!")
            print(f"🚨 1단계: {step1_name} → 2단계: {name}")
            print(f"🚨 1단계와 2단계 인증자가 다릅니다. 본인인증이 실패했습니다.")
            return jsonify({
                "error": "USER_MISMATCH",
                "message": "1단계와 2단계 인증자가 일치하지 않습니다. 본인인증이 실패했습니다."
            }), 400
        else:
            print("✅ 사용자 일치성 검증 성공")
        
        # Mock IDP 토큰 생성
        idp_payload = {
            "name": name,
            "rrn": rrn,
            "nonce": nonce,
            "iss": "mock-idp",
            "aud": "mvno-service"
        }
        
        idp_token = jwt_handler.create_jwt(idp_payload, expiry_seconds=300)  # 5분
        
        return jsonify({"idp_signed_token": idp_token}), 200
        
    except Exception as e:
        print(f"❌ Mock IDP 토큰 오류: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 기존 페이지들 (UI용)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/secure_auth")
def secure_auth():
    return render_template("secure_auth.html")

@app.route("/mvno_activation")
def mvno_activation():
    return render_template("mvno_activation.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # 테스트용 계정 정보
        if username == "admin" and password == "1234":
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다.")
    
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/admin")
def admin():
    # 총 사용자 수 (107만명)
    total_users = 1070000
    
    # 5개의 사용자 계정 데이터
    users = [
        {
            "username": "admin",
            "email": "admin@bcsmobile.com",
            "password": "********",
            "status": "활성",
            "join_date": "2024.01.15"
        },
        {
            "username": "manager1",
            "email": "manager1@bcsmobile.com",
            "password": "********",
            "status": "활성",
            "join_date": "2024.01.16"
        },
        {
            "username": "manager2",
            "email": "manager2@bcsmobile.com",
            "password": "********",
            "status": "활성",
            "join_date": "2024.01.17"
        },
        {
            "username": "support1",
            "email": "support1@bcsmobile.com",
            "password": "********",
            "status": "활성",
            "join_date": "2024.01.18"
        },
        {
            "username": "support2",
            "email": "support2@bcsmobile.com",
            "password": "********",
            "status": "활성",
            "join_date": "2024.01.19"
        }
    ]
    
    return render_template("admin.html", total_users=total_users, users=users)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
