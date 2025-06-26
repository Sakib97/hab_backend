from enum import Enum
class ReactionType(Enum):
    LIKE = "like"
    LOVE = "love"
    HAHA = "haha"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"

    @classmethod
    def from_str(cls, reaction_str):
        for reaction in cls:
            if reaction.value == reaction_str:
                return reaction.value
        raise ValueError(f"Unknown reaction type: {reaction_str}")
def is_valid_reaction(reaction):
    """
    Check if the given reaction is a valid reaction type.
    """
    try:
        ReactionType.from_str(reaction)
        return True
    except ValueError:
        return False
