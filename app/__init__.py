"""
Application initialization and configuration
"""

from flask import Flask
from flask_socketio import SocketIO

from app.services.config_manager import ConfigManager
from app.services.builder import MicroserviceBuilder

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('app.config.Config')

# Initialize SocketIO with threading for async support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize services
config_manager = ConfigManager()
builder = MicroserviceBuilder()


def emit_log(message):
    """Emit log messages to connected clients via SocketIO"""
    try:
        socketio.emit('log', {'message': message})
    except Exception as e:
        print(f"Error emitting log: {e}")


# Add log callback for real-time updates
builder.add_log_callback(emit_log)


def create_app():
    """
    Create and configure the Flask application

    Returns:
        tuple: (app, socketio) - Flask app and SocketIO instances
    """
    from app.routes import register_routes

    # Register all routes
    register_routes(app, socketio, config_manager, builder)

    return app, socketio