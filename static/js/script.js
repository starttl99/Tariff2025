// 데이터 업데이트 버튼 이벤트 리스너
document.addEventListener('DOMContentLoaded', function() {
    const updateDataBtn = document.getElementById('updateDataBtn');
    
    if (updateDataBtn) {
        updateDataBtn.addEventListener('click', function() {
            // 버튼 비활성화 및 텍스트 변경
            updateDataBtn.disabled = true;
            updateDataBtn.textContent = '업데이트 중...';
            
            // 데이터 업데이트 요청
            fetch('/update-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('데이터가 성공적으로 업데이트되었습니다. 페이지를 새로고침합니다.');
                    location.reload();
                } else {
                    alert('데이터 업데이트 중 오류가 발생했습니다.');
                    updateDataBtn.disabled = false;
                    updateDataBtn.textContent = '데이터 업데이트';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('데이터 업데이트 요청 중 오류가 발생했습니다.');
                updateDataBtn.disabled = false;
                updateDataBtn.textContent = '데이터 업데이트';
            });
        });
    }
});
