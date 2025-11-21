(function () {
    const buttons = document.querySelectorAll('.note-action');
    if (!buttons.length) {
        return;
    }

    const fab = document.getElementById('notes-fab');
    const toast = document.getElementById('note-toast');
    const toastMessage = document.getElementById('toast-message');
    const csrfToken = getCsrfToken();

    buttons.forEach((button) => {
        button.addEventListener('click', async () => {
            const hasNote = button.dataset.hasNote === 'true';
            const currentNote = button.dataset.note || '';
            const promptMessage = hasNote
                ? 'یادداشت خود را ویرایش کنید (برای حذف، متن را خالی بگذارید):'
                : 'یادداشت خود را وارد کنید:';

            const note = window.prompt(promptMessage, currentNote);
            if (note === null) {
                return;
            }

            // Show loading state
            button.disabled = true;
            button.textContent = '⏳ در حال ذخیره...';

            try {
                const response = await fetch(button.dataset.addUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        note: note,
                        next: window.location.pathname,
                    }),
                });

                if (!response.ok) {
                    throw new Error('Network error');
                }

                const data = await response.json();
                updateButtonState(button, data);
                updateFab(data.note_count);
                showToast(data.message, false);
            } catch (error) {
                showToast('خطا در ذخیره یادداشت', true);
            } finally {
                button.disabled = false;
            }
        });
    });

    function getCsrfToken() {
        const name = 'csrftoken=';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name)) {
                return decodeURIComponent(cookie.substring(name.length));
            }
        }
        return '';
    }

    function updateButtonState(button, data) {
        button.dataset.hasNote = data.has_note ? 'true' : 'false';
        button.dataset.note = data.note || '';

        if (data.has_note) {
            button.textContent = '📝 ویرایش';
            button.classList.remove('bg-indigo-100', 'text-indigo-700', 'hover:bg-indigo-200');
            button.classList.add('bg-gray-200', 'text-gray-700', 'hover:bg-gray-300');
        } else {
            button.textContent = '➕ افزودن';
            button.classList.remove('bg-gray-200', 'text-gray-700', 'hover:bg-gray-300');
            button.classList.add('bg-indigo-100', 'text-indigo-700', 'hover:bg-indigo-200');
        }
    }

    function updateFab(count) {
        if (!fab) {
            return;
        }
        
        const badge = fab.querySelector('span.bg-red-500');
        if (badge) {
            badge.textContent = count;
        }
        
        fab.dataset.count = count;
        if (count > 0) {
            fab.classList.remove('hidden');
        } else {
            fab.classList.add('hidden');
        }
    }

    function showToast(message, isError) {
        if (!toast || !toastMessage) {
            return;
        }
        
        toastMessage.textContent = message;
        toast.classList.remove('hidden');
        
        if (isError) {
            toast.classList.remove('bg-indigo-600');
            toast.classList.add('bg-red-600');
        } else {
            toast.classList.remove('bg-red-600');
            toast.classList.add('bg-indigo-600');
        }

        window.clearTimeout(showToast.timer);
        showToast.timer = window.setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }
})();
