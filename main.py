from app import app, db
# Above command imports app variable that is a member of the app package, which we created
# with the /app directory
# flask application instance is called app and a member
# of the app package

from app.models import User, Message

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User, 'Message': Message}