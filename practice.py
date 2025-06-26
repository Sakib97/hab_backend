# from util.encryptionUtil import xor_encode, xor_decode

# str1 = "dr@gmail.com"
# print("Original String:", str1)
# encoded_str = xor_encode(str1)
# print("Encoded String:", encoded_str)
# decoded_str = xor_decode(encoded_str)
# print("Decoded String:", decoded_str)

from util.reactionUtil import ReactionType, is_valid_reaction

def test_reaction_util():
    # Test valid reactions
    assert ReactionType.from_str("like") == ReactionType.LIKE
    assert ReactionType.from_str("love") == ReactionType.LOVE
    assert ReactionType.from_str("haha") == ReactionType.HAHA
    assert ReactionType.from_str("wow") == ReactionType.WOW
    assert ReactionType.from_str("sad") == ReactionType.SAD
    assert ReactionType.from_str("angry") == ReactionType.ANGRY

    # Test invalid reaction
    try:
        ReactionType.from_str("unknown")
    except ValueError as e:
        assert str(e) == "Unknown reaction type: unknown"

# test_reaction_util()

print(ReactionType.LIKE.value)
print(ReactionType.from_str("like"))

reaction = "likeee"
if is_valid_reaction(reaction):
    print(f"{reaction} is a valid reaction.")
else:
    print(f"{reaction} is not a valid reaction.")