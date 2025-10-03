// localstorage_id.js
// This script sets and retrieves a persistent user ID in LocalStorage
(function() {
    function generateSimpleId() {
        // Generates a random 4-character alphanumeric string
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let id = '';
        for (let i = 0; i < 4; i++) {
            id += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return id;
    }
    var userId = localStorage.getItem('moviematch_user_id');
    if (!userId) {
        userId = generateSimpleId();
        localStorage.setItem('moviematch_user_id', userId);
    }
    // Expose userId for other scripts
    window.moviematchUserId = userId;
})();
