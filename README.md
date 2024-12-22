# Weatherpia Assignment - 회원 관리 서비스 (REST API)

## 프로젝트 개요
- Flask(파이썬)와 MariaDB로 만든 간단한 회원 관리 시스템
- 회원 정보(`ID`, `Password`, `Name`, `Nickname`, `Email`, `Grade`)를 
  등록(C), 조회(R), 수정(U), 삭제(D)할 수 있음
- HTML 페이지와 REST API 두 가지 방식 지원
- Swagger UI(`/apidocs`)를 통해 API 문서 확인 가능
- 회원 목록: **이름 정렬**, **등급 정렬**, **페이지네이션**

## Project Overview
- A simple **Member Management System** built with **Flask (Python)** and **MariaDB**
- CRUD operations (Create, Read, Update, Delete) for members
- Both **HTML pages** and **REST API** are available
- Swagger UI at `/apidocs` for API documentation
- Member list supports **sorting by name or grade** and **pagination**

---

## 폴더 구조

1. **app.py**  
   - Flask 메인 파일: DB 연결, HTML 라우트(`/`, `/members`, `/update/<id>`, etc.),  
   - REST API(`/api/members`), Swagger UI 설정(`/apidocs`)  
2. **seed_data.py (Optional)**  
   - `python seed_data.py` 실행 시, 100명의 임의 회원 생성  
3. **templates** 폴더:  
   - `main.html` (회원 등록), `list.html` (목록, 정렬 & 페이징), `update.html` (수정)  
4. **static/swagger.json (Optional)**  
   - Swagger UI에서 불러올 API 문서
5. **README.md**  
   - 프로젝트 소개

---

## 주요 기능

1. **회원 등록 (Create)**
   - **HTML**: `GET /` → Form → `POST /`  
   - **REST**: `POST /api/members` (JSON Body)
2. **회원 조회 (Read)**
   - **HTML**: `GET /members` + 정렬&페이지네이션
   - **REST**: `GET /api/members`, `GET /api/members/<id>`
3. **회원 수정 (Update)**
   - **HTML**: `GET/POST /update/<id>`
   - **REST**: `PUT /api/members/<id>`
4. **회원 삭제 (Delete)**
   - **HTML**: `POST /delete/<id>`
   - **REST**: `DELETE /api/members/<id>`
5. **정렬 / 페이지네이션**
   - 이름(가나다), 등급(높은/낮은 순)
   - 페이지별로 10명씩 표시
6. **Swagger UI**
   - `/apidocs`에서 API 문서 확인
7. **seed_data.py** (Optional)
   - 100명 임의 회원 삽입 스크립트

---

## 설치 & 실행

1. **DB 준비**: `members_db` 생성, `members` 테이블
2. **가상환경(옵션)**: `python -m venv venv && .\venv\Scripts\activate.ps1`
3. **라이브러리 설치**: `pip install flask pymysql flask-swagger-ui`
4. **(선택) 더미 데이터**: `python seed_data.py`
5. **서버 실행**: `python app.py`
6. **접속**:
   - HTML: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
   - 회원 목록: [http://127.0.0.1:5000/members](http://127.0.0.1:5000/members)
   - Swagger UI: [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)

---

## 주의 사항
- 정렬/페이지 파라미터는 기본 수준의 화이트리스트 처리
- 예외 처리는 최소화
- 배포 시 Docker 등 고려

---

이 프로젝트는 상업용 배포가 아닌, 과제용 소스코드로 작성되었습니다.

