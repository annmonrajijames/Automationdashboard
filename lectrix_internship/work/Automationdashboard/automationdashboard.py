import os
from pptx import Presentation
from pptx.util import Inches, Pt
folder_path = r"c:\Users\annmon.james\lectrix_internship\work\Automationdashboard\presentation"
# Define the analysis results (as an example)
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
analysis_results = {
    "Total time taken for the ride": "02:30",
    "Actual Ampere-hours (Ah)": "-0.496635",
    "Actual Watt-hours (Wh)": "-25.81896295027778",
    "Starting SoC (Ah)": "33.91",
    "Ending SoC (Ah)": "34.433",
    "Total distance covered (in kilometers)": "120",
    "WH/KM": "-40.360253303742816",
    "Total SOC consumed": "1.0%",
    "Mode": "Eco mode"
}

# Specify the path to the graph image
graph_image_path = r"c:\Users\annmon.james\lectrix_internship\work\Automationdashboard\graph.png"
def generate_presentation(folder_path, analysis_results, graph_image_path):
    """
    Generates a PowerPoint presentation from analysis results.

    Parameters:
    - folder_path: The path to save the presentation.
    - analysis_results: A dictionary containing the analysis results.
    - graph_image_path: Path to the graph image to include in the presentation.
    """
    # Create a new PowerPoint presentation
    prs = Presentation()

    # Extract folder name from folder_path
    folder_name = os.path.basename(folder_path)

    # Add title slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text = f"Analysis Results from Folder - {folder_name}"
    subtitle.text = "Automated Analysis Summary"

    # Add analysis results slide
    for key, value in analysis_results.items():
        bullet_slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(bullet_slide_layout)
        shapes = slide.shapes

        title_shape = shapes.title
        body_shape = shapes.placeholders[1]

        title_shape.text = "Analysis Results"
        tf = body_shape.text_frame
        tf.text = f"{key}: {value}"

    # Add graph image slide
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)

    slide.shapes.add_picture(graph_image_path, Inches(1), Inches(1), width=prs.slide_width - Inches(2))

    # Save the presentation
    output_file_name = os.path.join(folder_path, f"analysis_{folder_name}.pptx")
    prs.save(output_file_name)

generate_presentation(folder_path, analysis_results, graph_image_path)
