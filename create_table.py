# temp file to force create the tables 
# runfile command: python create_table.py 
# run from terminal without venv
from core.database import Base, engine
# from model.userModel import UserModel
# from model.articleModel import ArticleModel
# from model.notificationModel import EditorNotification
# from model.noteModel import NoteSubject, NoteMessage
from model.commentModel import ArticleReactionModel, CommentModel, CommentReactionModel, CommentReportModel

# Create the tables
Base.metadata.create_all(bind=engine)