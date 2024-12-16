// 회원 등록
document.getElementById('memberForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        user_id: document.getElementById('user_id').value,
        password: document.getElementById('password').value,
        name: document.getElementById('name').value,
        nickname: document.getElementById('nickname').value,
        email: document.getElementById('email').value,
        grade: document.getElementById('grade').value
    };

    try {
        const response = await fetch('/api/members', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error(error);
        alert('회원 등록 중 오류가 발생했습니다.');
    }
});
