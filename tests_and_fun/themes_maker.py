import matplotlib.patches as patches
import matplotlib.pyplot as plt


def parse_and_visualize_weird_palette(palette_str):
    # Split the input string into lines
    lines = palette_str.split(";")

    # Initialize an empty dictionary to hold the color information
    colors = {}

    # Parse each line
    for line in lines:
        if not line.strip():
            continue  # Skip empty lines
        # Split each line into name and color value
        name, color = line.split(":")
        # Remove leading/trailing whitespace and replace dashes with spaces in the name for readability
        name = name.strip().replace("--color-", "").replace("-", " ").title()
        color = color.strip()
        # Add to the colors dictionary
        colors[name] = color

    # Now, we have the colors dictionary filled, we can visualize it
    # Create a figure and a grid of subplots
    fig, ax = plt.subplots(figsize=(10, 8))

    # Remove the axes
    ax.axis("off")

    # Title
    ax.set_title("Weird Color Palette Visualization", fontsize=16)

    # Plot each color as a rectangle
    for i, (name, color) in enumerate(colors.items()):
        row = i // 4
        col = i % 4
        rect = patches.Rectangle(
            (col * 2.5, row * -1.5),
            2,
            1,
            linewidth=1,
            edgecolor="none",
            facecolor=color,
        )
        ax.add_patch(rect)
        ax.text(
            col * 2.5 + 1,
            row * -1.5 + 0.5,
            name,
            ha="center",
            va="center",
            fontsize=9,
            color="white" if i < 14 else "black",
            weight="bold",
        )

    # Adjust the limits and aspect of the plot
    ax.set_xlim(0, 10)
    ax.set_ylim(-6, 1)
    ax.set_aspect(1)

    plt.show()


# Example of a weird palette
weird_palette_str = """
--color-primary: #88c999;
--color-primary-light: #cc8899;
--color-secondary: #987654;
--color-accent: #fe01b1;
--color-bg-dark: #013370;
--color-bg-dark-tone: #650021;
--color-bg-dark-tone-panel: #feae17;
--color-bg-dark-code-block: #bada55;
--color-bg-light: #420420;
--color-bg-light-tone: #133337;
--color-bg-light-code-block: #065535;
--color-bg-light-tone-panel: #511845;
--color-bg-dark-discussion: #170e4b;
--color-bg-dark-discussion-odd: #331a38;
--color-bg-light-discussion: #f4c2c2;
--color-bg-light-discussion-odd: #fae7b5;
"""
weird_palette_str = """
--color-primary: #0e8ef0;
--color-primary-light: #3dabff;
--color-secondary: #0fd974;
--color-accent: #f0700e;
--color-bg-dark: #132e59;
--color-bg-dark-tone: #25477d;
--color-bg-dark-tone-panel: #4367a3;
--color-bg-dark-code-block: #2254a7;
--color-bg-light: #e2edff;
--color-bg-light-tone: #b9d2f7;
--color-bg-light-code-block: #cad7ed;
--color-bg-light-tone-panel: #8fb5ef;
--color-bg-dark-discussion: #435E8A;
--color-bg-dark-discussion-odd: #284471;
--color-bg-light-discussion: #c5d8f8;
--color-bg-light-discussion-odd: #d6e7ff;
"""
parse_and_visualize_weird_palette(weird_palette_str)
