from flask import Flask, render_template, request, session
from flask_socketio import SocketIO
from backend.agents.session.service_agent_session import ServiceAgentSession
import json
import threading

# Initialize a lock
user_sessions_lock = threading.Lock()
user_sessions = {}

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
socketio = SocketIO(app, async_mode='eventlet')

# Default configuration
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': 30011,
    # 'agent_name': 'esp_decision_assistant',
    'agent_name': 'telco_network_support',
    'thinking_file': '/tmp/agent_thinking.txt'
}


def get_agent_session():
    if 'agent_session' not in session:
        # Use session variables only within request context
        host = session.get('host', DEFAULT_CONFIG['host'])
        port = session.get('port', DEFAULT_CONFIG['port'])
        agent_name = session.get('agent_name', DEFAULT_CONFIG['agent_name'])
        session['agent_session'] = ServiceAgentSession(
            host=host,
            port=port,
            agent_name=agent_name
        )
    return session['agent_session']


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Update configuration based on user input
        session['host'] = request.form.get('host', DEFAULT_CONFIG['host'])
        session['port'] = int(request.form.get('port', DEFAULT_CONFIG['port']))
        session['agent_name'] = request.form.get('agent_name', DEFAULT_CONFIG['agent_name'])
        # Initialize agent session with new config
        session['agent_session'] = None
    return render_template('index.html', agent_name=session.get('agent_name', DEFAULT_CONFIG['agent_name']))


# noinspection PyUnresolvedReferences
@socketio.on('user_input')
def handle_user_input(data):
    user_input = data.get('message')
    sly_data = data.get('sly_data')

    # Get the Socket.IO session ID
    sid = request.sid

    # Retrieve or initialize user-specific data
    with user_sessions_lock:
        user_data = user_sessions.get(sid)
        if not user_data:
            # Use the current session values for agent configuration
            host = session.get('host', DEFAULT_CONFIG['host'])
            port = session.get('port', DEFAULT_CONFIG['port'])
            agent_name = session.get('agent_name', DEFAULT_CONFIG['agent_name'])
            agent_session = ServiceAgentSession(
                host=host,
                port=port,
                agent_name=agent_name
            )
            session_id = None
            user_data = {
                'agent_session': agent_session,
                'session_id': session_id,
                'last_logs_length': 0  # Initialize logs length
            }
            user_sessions[sid] = user_data
        else:
            agent_session = user_data['agent_session']
            session_id = user_data['session_id']

    chat_request = {
        'session_id': session_id,
        'user_input': user_input
    }

    if sly_data:
        chat_request['sly_data'] = json.loads(sly_data)

    chat_response = agent_session.chat(chat_request)
    print(f"chat_response: {chat_response}")

    if not session_id:
        session_id = chat_response.get('session_id')
        user_data['session_id'] = session_id

    # Start a background task and pass necessary data
    socketio.start_background_task(target=background_response_handler, sid=sid)


# noinspection PyUnresolvedReferences
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    with user_sessions_lock:
        if sid in user_sessions:
            del user_sessions[sid]
    print(f"Client disconnected: {sid}")


def background_response_handler(sid):
    while True:
        # Retrieve user-specific data
        with user_sessions_lock:
            user_data = user_sessions.get(sid)
        if not user_data:
            print(f"No user data found for sid {sid}")
            return

        agent_session = user_data['agent_session']
        session_id = user_data['session_id']
        last_logs_length = user_data.get('last_logs_length', 0)

        logs_request = {'session_id': session_id}
        logs_response = agent_session.logs(logs_request)

        # Get logs and chat response
        logs = logs_response.get('logs', [])
        chat_response = logs_response.get('chat_response')

        # Emit new logs to the client
        new_logs = logs[last_logs_length:]
        for log in new_logs:
            socketio.emit('agent_log', {'log': log}, room=sid)
        last_logs_length = len(logs)

        # Update last_logs_length in user_data
        with user_sessions_lock:
            user_data['last_logs_length'] = last_logs_length

        # **Print chat_response for debugging**
        print(f"chat_response: {chat_response}")

        # Check if assistant's response is available
        if chat_response:
            socketio.emit('agent_response', {'message': chat_response}, room=sid)
            break  # Exit the loop after sending the response

        # Sleep before the next poll to prevent excessive requests
        socketio.sleep(1)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=5432)
