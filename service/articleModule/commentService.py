from fastapi import HTTPException, Request, status, Depends
from service.userModule.userService import get_current_user_profile
from model.articleModel import ArticleModel
from sqlalchemy.orm import Session
from util.reactionUtil import is_valid_reaction
from model.commentModel import ArticleReactionModel, CommentReactionModel, CommentModel
from datetime import datetime
from sqlalchemy import func

# article or comment reaction submission
def article_or_comment_react(request: Request,
                             reactPlace: str,
                             content_id: int,
                             reaction_type: str,
                             db: Session):
    """
    Adds, updates, or removes a reaction to an article or a comment.
    If the user reacts with the same type, the reaction is removed (toggle off).
    If the user reacts with a different type, the reaction is updated.
    If the user has no reaction, a new one is created.
    """
    try:
        if reactPlace not in ["article", "comment"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid react place")
        current_user, user_email, exp = get_current_user_profile(request, db)
        if not is_valid_reaction(reaction_type):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reaction type")

        ReactionModel = None
        content_filter = None

        if reactPlace == "article":
            # Check if article exists
            article = db.query(ArticleModel).filter(ArticleModel.article_id == content_id).first()
            if not article:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
            ReactionModel = ArticleReactionModel
            content_filter = (ArticleReactionModel.article_id == content_id)
        elif reactPlace == "comment":
            # Implement comment reaction logic
            # 1. Check if comment exists
            comment = db.query(CommentModel).filter(CommentModel.comment_id == content_id).first()
            if not comment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
            # 2. Set ReactionModel = CommentReactionModel
            ReactionModel = CommentReactionModel
            # 3. Set content_filter
            content_filter = (CommentReactionModel.comment_id == content_id)

        # Check if the user has any existing reaction to the content
        existing_reaction = db.query(ReactionModel).filter(
            content_filter,
            ReactionModel.user_email == user_email
        ).first()

        if existing_reaction:
            # User has an existing reaction
            if existing_reaction.reaction_type == reaction_type:
                # User is toggling off the same reaction, so delete it
                db.delete(existing_reaction)
                db.commit()
                return {"message": "Reaction removed"}
            else:
                # User is changing their reaction, so update it
                existing_reaction.reaction_type = reaction_type
                db.commit()
                db.refresh(existing_reaction)
                return {"message": "Reaction updated", "reaction": existing_reaction.reaction_type}
        else:
            # User has no existing reaction, so create a new one
            new_reaction_data = {
                
                'user_email': user_email,
                'reaction_type': reaction_type,
                'user_slug': current_user.user_slug,
                'created_at': datetime.now()
            }
            if reactPlace == "article":
                new_reaction_data['article_id'] = content_id
            elif reactPlace == "comment":
                new_reaction_data['comment_id'] = content_id

            new_reaction = ReactionModel(**new_reaction_data)
            db.add(new_reaction)
            db.commit()
            db.refresh(new_reaction)
            return {"message": "Reaction added", "reaction": new_reaction.reaction_type}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the reaction."
        )

def get_reaction_counts(
    db: Session,
    reactPlace: str,
    content_id: int,
    request: Request = None
):
    """
    Gets the reaction counts for an article or comment.
    If a user is logged in (checked via optional request), it also returns their specific reaction.
    """
    try:
        if reactPlace not in ["article", "comment"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid react place")

        ReactionModel = None
        content_filter = None

        if reactPlace == "article":
            ReactionModel = ArticleReactionModel
            content_filter = (ArticleReactionModel.article_id == content_id)
        elif reactPlace == "comment":
            ReactionModel = CommentReactionModel
            content_filter = (CommentReactionModel.comment_id == content_id)

        # Get counts of each reaction type
        reaction_counts = db.query(
            ReactionModel.reaction_type,
            func.count(ReactionModel.reaction_type).label("count")
        ).filter(content_filter).group_by(ReactionModel.reaction_type).all()

        reactions_dict = {reaction: count for reaction, count in reaction_counts}
        total_reactions = sum(reactions_dict.values())

        # Check for the current user's reaction if they are logged in
        user_reaction = None
        user_email = None
        try:
            if request and request.headers.get("Authorization"):
                _, user_email, _ = get_current_user_profile(request, db)
        except HTTPException:
            # This handles cases where the token is missing, expired, or invalid.
            # We proceed as an anonymous user.
            user_email = None

        if user_email:
            reaction_obj = db.query(ReactionModel).filter(
                content_filter,
                ReactionModel.user_email == user_email
            ).first()
            if reaction_obj:
                user_reaction = reaction_obj.reaction_type

        return {
            "reactions": reactions_dict,
            "total_reactions": total_reactions,
            "user_reaction": user_reaction
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching reactions."
        )