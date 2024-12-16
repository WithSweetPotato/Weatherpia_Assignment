document.addEventListener('DOMContentLoaded', () => {
    // HTML에서 `member` 데이터를 JSON 형식으로 가져오기
    const memberData = JSON.parse(document.getElementById('edit-member-form').dataset.member);

    // 폼에 기존 회원 데이터 채우기
    document.getElementById('user_id').value = memberData.user_id;
    document.getElementById('name').value = memberData.name;
    document.getElementById('nickname').value = memberData.nickname;
    document.getElementById('email').value = memberData.email;
    document.getElementById('grade').value = memberData.grade;

    // 저장 버튼 클릭 이벤트 처리
    document.getElementById('save-button').addEventListener('click', () => {
        const updatedMember = {
            name: document.getElementById('name').value,
            nickname: document.getElementById('nickname').value,
            email: document.getElementById('email').value,
            grade: document.getElementById('grade').value
        };

        fetch(`/api/members/${memberData.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedMember),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "회원 정보가 성공적으로 수정되었습니다.") {
                alert("회원 정보가 업데이트되었습니다!");
            } else {
                alert(`오류 발생: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("회원 정보를 업데이트하는 중 오류가 발생했습니다.");
        });
    });
});
