# 🔔 챙겨봇

### 슬랙에서 반복 업무를 놓치지 않도록 도와주는 리마인더 봇

매일 챙겨야 할 업무, 이제 사람이 아니라 챙겨봇이 챙겨줄게요.


## 📌 프로젝트 정보
- **슬랙봇(Slack Bot) 프로젝트**
- **단기 계약직 근무 당시, 타 팀 요청으로 혼자 설계 및 개발**
- 포트폴리오 용도로 개인적으로 재구현한 프로젝트


## 🧩 프로젝트 주제

- **슬랙 기반 반복 업무 리마인드 자동화 봇**
  - 사용자가 직접 문구와 담당자를 입력하여 리마인드 생성
  - 지정된 기간 동안 매일 자동으로 담당자에게 알림 전송
  - 진행 현황을 한눈에 확인하고, 작업 완료 시 자동 종료되는 구조


## 💡 프로젝트 기획 의도

슬랙 사용 빈도가 높은 조직 환경에서는 **반복적으로 확인해야 하는 업무를 사람이 직접 챙기는 데 한계**가 있었습니다.

- 실무 환경에서의 문제점
  - 매일 반복되는 업무를 사람이 직접 멘션
  - 담당자별 진행 상황을 한눈에 파악하기 어려움
  - 작업이 끝났음에도 불필요한 알림이 계속 전송되는 문제

- 챙겨봇의 목표
  - **슬랙 안에서 모든 리마인드 흐름을 해결**
  - Slack App Shortcut + Modal을 활용해 **복잡한 설정 없이 리마인드 생성**
  - 담당자별 진행 상태를 명확하게 관리
  - 작업 완료 시 자동 종료로 불필요한 알림 최소화


## 🛠️ 개발 환경

### 기술 스택

<div style="overflow-x:auto;">
<table style="width: 100%; border-collapse: collapse;">
  <tr>
    <td style="padding: 10px;">Backend</td>
    <td style="padding: 10px;">
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" />
        <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" />
        <img src="https://img.shields.io/badge/Bolt-611f69?style=flat&logo=slack&logoColor=white" />
    </td>
  </tr>
    <tr>
        <td style="padding: 10px;">Workflow / Scheduler</td>
        <td style="padding: 10px;">
            <img src="https://img.shields.io/badge/Apache%20Airflow-017CEE?style=flat&logo=Apache%20Airflow&logoColor=white"/>
        </td>
      </tr>
    <tr>
  <tr>
    <td style="padding: 10px;">DB</td>
    <td style="padding: 10px;">
        <img src="https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat&logo=mongodb&logoColor=white" />
    </td>
  </tr>
<tr>
    <td style="padding: 10px;">External Services</td>
    <td style="padding: 10px;">
        <img src="https://img.shields.io/badge/Notion-FFFFFF?style=flat&logo=notion&logoColor=black"/>
        <img src="https://img.shields.io/badge/Slack-4A154B?style=flat&logo=slack&logoColor=white" />
    </td>
  </tr>
<tr>
    <td style="padding: 10px;">Tools</td>
    <td style="padding: 10px;">
        <img src="https://img.shields.io/badge/Github-181717?style=flat&logo=github&logoColor=white"/>
        <img src="https://img.shields.io/badge/Postman-FF6C37?style=flat-square&logo=Postman&logoColor=white"/>
    </td>
  </tr>
</table>
</div>


## ✨ 핵심 기능

### Slack App Shortcut 기반
- 리마인드 생성
- 리마인드 삭제
- 리마인드 진행 상황 조회
  - 모달을 통해 아래 정보 제공
    - 조회한 리마인드의 문구
    - 전체 작업률
    - 진행 중인 담당자 리스트
    - 작업 완료한 담당자 리스트

  
|리마인드 생성|리마인드 삭제|
|:----:|:----:|
|<img width="400" height="225" src="https://github.com/user-attachments/assets/8cb6c91b-235a-486d-9eb3-5af85d1e2612">|<img width="400" height="225" src="https://github.com/user-attachments/assets/76cabdca-7268-43e0-a3c2-27996edddbf2">|
|**리마인드 진행 상황 조회**|
|<img width="400" height="225" src="https://github.com/user-attachments/assets/b104b16f-42c7-4d5e-b552-d1627fbd37d1">|


### 자동 리마인드 알림
- 평일 오전 10시 리마인드 로직 실행
- 리마인드 기간에 포함될 경우:
  - 담당자 멘션
  - 설정한 문구와 함께 스레드에 전송
  - 리마인드 종료 전날에는 종료 예정 문구도 함께 스레드에 전송
- 리마인드 기간이 종료된 경우:
  - 리마인드 종료 문구 스레드에 전송

|리마인드 알림|리마인드 종료 예정|
|:----:|:----:|
|<img width="400" height="225" src="https://github.com/user-attachments/assets/a09f1df2-b726-4afd-bfb9-651cd7d89201">|<img width="400" height="225" src="https://github.com/user-attachments/assets/2e3fc186-5446-40cf-b356-02f401604c42">|
|**리마인드 종료**|
|<img width="400" height="225" src="https://github.com/user-attachments/assets/788abd06-785a-42ce-8496-66983c65af6e">|

### 작업 완료 버튼
- 리마인드 메시지에 **작업 완료 버튼** 제공
- 담당자가 작업 완료 버튼 클릭 시:
  - 해당 담당자는 더 이상 알림 수신 ❌
  - 기존 리마인드 알림 스레드 내 멘션 제거
    - 슬랙 스레드 특성상 이전 멘션으로 인한 알림 이슈 해결

|작업 완료|모든 담당자 작업 완료 시|
|:----:|:----:|
|<img width="400" height="225" src="https://github.com/user-attachments/assets/23fd1bf3-3b69-4c92-9a18-c4ff9197c273">|<img width="400" height="225" src="https://github.com/user-attachments/assets/0cde4d77-8610-44dd-81b1-30d29e6e1422">|

### 리마인드 생성 검증 실패 시 DM 전송
- 리마인드 생성 시 검증에 실패할 경우 슬랙 개인 메시지 전송
- 리마인드 관리 정책
  - **한 채팅당 하나의 리마인드**만 생성 가능
    - 여러 리마인드로 인한 현황 조회 오류 방지
    - 이미 리마인드가 존재할 경우 리마인드 삭제 후 생성 가능
    - **리마인드 자동 삭제 기준**
      - 모든 담당자가 작업을 완료했을 경우
      - 리마인드 종료일이 지난 후 스레드에 종료 안내가 전송된 경우
  - 리마인드 시작일은 종료일 이전만 가능
  - 리마인드 종료일은 생성일 이후만 가능

|검증 실패|
|:----:|
|<img width="400" height="225" src="https://github.com/user-attachments/assets/835a5408-27af-4921-8b39-5eef995c9962">|
