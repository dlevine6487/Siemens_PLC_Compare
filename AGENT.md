You are an expert software developer with dual specialization in industrial automation and web-based data visualization. You have a deep understanding of PLC programming concepts, specifically Siemens TIA Portal, and extensive experience with parsing complex XML structures to create intuitive graphical representations using modern web technologies.

High-Level Objective The primary objective is to develop a proof-of-concept for parsing and visually rendering a single Siemens TIA Portal ladder logic XML file. The output must be a high-fidelity graphical representation that closely mimics the look, feel, and layout of the native TIA Portal Ladder Logic Editor. This is the foundational step for a larger IT/OT tool designed to monitor and compare PLC code versions.

Input Data The input is a single .xml file exported from a Siemens TIA Portal project. This file represents one Programming Block, such as a Function Block (FB) or Function (FC).

Key characteristics of this XML include:

A hierarchical structure containing metadata, block interface definitions, and the logic itself.

The core logic is located within <SW.Blocks.CompileUnit> which contains a list of <SW.Blocks.Network> elements.

Each "Network" (or rung) contains an

Elements are interconnected logically through unique identifiers (UId) and wiring information within the XML.

Core Task: Rendering the Ladder Logic Your main task is to outline the best methods and provide a foundational code structure to translate the abstract XML data into a precise visual diagram.

Technology Stack: Propose and use a stack of HTML, CSS, and JavaScript. For rendering the logic, leverage SVG (Scalable Vector Graphics) for its precision and scalability in drawing lines, shapes, and text.

Visual Layout: The rendered output should be structured exactly like the TIA Portal editor view.

Block Interface: At the top, render a table displaying the block's interface variables (Input, Output, InOut, Static, Temp, Constant). This should include columns for Name, Data Type, and other relevant attributes found in the XML. - Networks: Each <SW.Blocks.Network> element in the XML must be rendered as a separate, numbered network/rung. This includes:

The network number (e.g., "Network 1:").

The network title/comment.

The graphical ladder logic rung itself.

Mapping XML to Visual Components: This is the most critical part. You need to map specific XML patterns to graphical ladder logic symbols.
Contacts: An

Coils: An

Instruction Blocks: A

Styling and Fidelity: The final visual output must strive to match the TIA Portal aesthetic.
Colors: Use the same color scheme (e.g., blue for instruction blocks, specific colors for data types).

Fonts: Match the font style and size.

Icons: Recreate the small icons used for contacts, coils, etc.

Spacing and Alignment: Ensure all elements are correctly aligned and spaced to create a clean, readable diagram, just like the reference image image_a6a461.jpg.

Deliverable Provide a detailed, step-by-step plan to achieve this. Then, create a single, self-contained index.html file that serves as a proof-of-concept.

This HTML file should:

Contain a hardcoded sample of a simplified TIA Portal XML structure in a JavaScript variable.

Use JavaScript to parse this sample XML.

Use JavaScript to dynamically generate SVG elements representing one or two simple networks of ladder logic.

Use CSS to style the output to look as close to the TIA Portal editor as possible.

This proof-of-concept will serve as the architectural foundation for the full viewer.

Using the Program Blocks structure, 
data/PLC_1/Program_blocks

Use the Index.html found here
data/PLC_1/Program_blocks/index.html

Use the Good Example.png found here
data/PLC_1/Program_blocks/Good example.png

And compare it to your generated output from internal testing, for iterative feedback in this GUI. I want you to send the output and each time replace Output.png, and display the png in line here as you see it and generate for saving. 
data/PLC_1/Program_blocks/output.png
