/* global jQuery, console */
(function ($) {
    var socket = null,
        name = null;

    function sendMessage(msg) {
        socket.send(JSON.stringify({
            message: msg,
            user: name
        }));
    }

    function addMessage(msg) {
        var wrapper = $('<div>')
                .addClass('line')
                .append($('<span>').addClass('user').text(msg.user))
                .append($('<span>').addClass('text').text(msg.message));
        $('#messages').append(wrapper);
    }

    $('#main form').on('submit', function (e) {
        var text = $('#message').val();
        e.preventDefault();
        if (socket) {
            // Log local message
            addMessage({user: name, message: text});
            // Send message to the socket
            sendMessage(text);
            $('#message').val('');
        } else {
            name = $('#name').val();
            socket = new WebSocket($(this).data('socket'));
            socket.onopen = function () {
                $('#name').prop('hidden', true).prop('disabled', true);
                $('#connect').prop('hidden', true).prop('disabled', true);
                $('#label').text(name).prop('hidden', false);
                $('#message').prop('hidden', false).prop('disabled', false);
                $('#send').prop('hidden', false).prop('disabled', false);
            };
            socket.onclose =  function () {
                $('#label').prop('hidden', true);
                $('#message').prop('hidden', true).prop('disabled', true);
                $('#send').prop('hidden', true).prop('disabled', true);
                $('#name').prop('hidden', false).prop('disabled', false);
                $('#connect').prop('hidden', false).prop('disabled', false);
                socket = null;
                name = null;
            };
            socket.onmessage = function (e) {
                addMessage(JSON.parse(e.data));
            };
        }
    });

})(jQuery);
