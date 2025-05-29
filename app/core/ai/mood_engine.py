def detect_mood(input_text: str) -> str:
    """
    Analyze the input and return a simplified mood.

    Args:
        input_text (str): Raw user input

    Returns:
        str: One of ['neutral', 'sad', 'happy', 'frustrated', 'excited']
    """
    text = input_text.lower()

    # Basic keyword mapping — replace with ML later
    if any(word in text for word in ["sad", "tired", "depressed", "down"]):
        return "sad"
    elif any(word in text for word in ["angry", "frustrated", "annoyed", "stuck"]):
        return "frustrated"
    elif any(word in text for word in ["yay", "awesome", "great", "happy"]):
        return "happy"
    elif any(word in text for word in ["let's go", "ready", "hype", "excited"]):
        return "excited"
    else:
        return "neutral"

def mood_wrapped_prompt(prompt: str, mood: str) -> str:
    """
    Wrap the original prompt with a mood-based instruction.

    Args:
        prompt (str): User prompt
        mood (str): Detected mood

    Returns:
        str: Adjusted prompt string
    """
    if mood == "sad":
        return f"Respond with compassion and softness: {prompt}"
    elif mood == "frustrated":
        return f"Respond with patience and clarity: {prompt}"
    elif mood == "happy":
        return f"Respond positively and warmly: {prompt}"
    elif mood == "excited":
        return f"Respond with enthusiasm and energy: {prompt}"
    return prompt