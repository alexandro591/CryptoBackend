import random

def generateNonce():
    """Generate pseudorandom number."""
    return random.randint(0, 100000000)