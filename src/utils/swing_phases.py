from enum import Enum

class SwingPhase(Enum):
    P1_ADDRESS = "P1: Address"
    P2_TAKEAWAY = "P2: Takeaway"
    P3_HALFWAY_BACK = "P3: Halfway Back"
    P4_TOP = "P4: Top"
    P5_EARLY_DOWN = "P5: Early Downswing"
    P6_PRE_IMPACT = "P6: Pre-Impact"
    P7_IMPACT = "P7: Impact"
    P8_RELEASE = "P8: Release"
    P9_FOLLOW = "P9: Follow Through"
    P10_FINISH = "P10: Finish"

# Detailed descriptions for each phase
PHASE_DESCRIPTIONS = {
    SwingPhase.P1_ADDRESS: [
        "proper athletic golf stance with knees flexed",
        "spine tilted forward from hips at address",
        "arms hanging naturally at address",
        "weight distributed evenly between feet",
        "poor posture with rounded back",
        "knees too straight at address",
        "weight too much on toes or heels"
    ],
    SwingPhase.P2_TAKEAWAY: [
        "club moves back low and slow",
        "shoulders rotating while arms stay connected",
        "club head stays outside hands",
        "maintaining triangle between arms and chest",
        "lifting club too quickly",
        "breaking wrists too early",
        "club moving too far inside"
    ],
    SwingPhase.P3_HALFWAY_BACK: [
        "club shaft parallel to ground and target line",
        "hands at hip height in backswing",
        "good shoulder rotation with stable head",
        "maintaining spine angle",
        "lifting arms instead of turning",
        "loss of spine angle",
        "swaying off the ball"
    ],
    SwingPhase.P4_TOP: [
        "club shaft parallel to ground at top",
        "left arm reasonably straight",
        "90 degree shoulder turn",
        "weight maintained on inside of back foot",
        "over-rotation at top",
        "collapsing left arm",
        "swaying or lifting up"
    ],
    SwingPhase.P5_EARLY_DOWN: [
        "lower body leads the downswing",
        "arms dropping into slot",
        "maintaining width in downswing",
        "good weight shift to lead side",
        "casting club from top",
        "arms leading the downswing",
        "losing spine angle"
    ],
    SwingPhase.P6_PRE_IMPACT: [
        "hips open at impact",
        "hands ahead of club head",
        "maintaining spine angle",
        "weight shifted to lead side",
        "early extension",
        "flipping hands through impact",
        "hanging back on trail foot"
    ],
    SwingPhase.P7_IMPACT: [
        "hands leading club at impact",
        "hips rotated 45 degrees open",
        "weight forward at impact",
        "shaft leaning forward",
        "flipping at impact",
        "weight on back foot",
        "casting through impact"
    ],
    SwingPhase.P8_RELEASE: [
        "full extension of arms after impact",
        "rotating body through impact",
        "maintaining spine angle",
        "good weight transfer",
        "early release",
        "stopping body rotation",
        "falling backward"
    ],
    SwingPhase.P9_FOLLOW: [
        "arms extending toward target",
        "body rotating toward target",
        "weight fully shifted forward",
        "maintaining balance",
        "chicken wing left arm",
        "incomplete hip turn",
        "poor weight transfer"
    ],
    SwingPhase.P10_FINISH: [
        "belt buckle facing target",
        "chest facing target",
        "weight on front foot",
        "balanced finish position",
        "falling backward",
        "incomplete turn through",
        "poor balance at finish"
    ]
}
