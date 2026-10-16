"""Build the hardware setup guide for the Smart Voice Controlled Dustbin."""

from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image as RLImage,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "hardware-setup-guide.pdf"
PAGE_W, PAGE_H = A4
NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2B6F9F")
PALE = colors.HexColor("#EEF5F8")
MID = colors.HexColor("#D9E3E8")
TEXT = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#536573")


def image(path, max_w=170 * mm, max_h=90 * mm):
    path = ROOT / path
    with Image.open(path) as img:
        w, h = img.size
    scale = min(max_w / w, max_h / h)
    # Downsample source photographs/screenshots to the resolution needed for
    # print. This keeps the repository PDF compact without visible blur.
    target_w = max(1, int((w * scale / 72) * 180))
    target_h = max(1, int((h * scale / 72) * 180))
    cache = ROOT / "tmp" / "hardware_guide_assets"
    cache.mkdir(parents=True, exist_ok=True)
    cached = cache / f"{path.stem}-{target_w}x{target_h}.jpg"
    if not cached.exists():
        with Image.open(path) as img:
            img.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS).save(cached, "JPEG", quality=86, optimize=True)
    return RLImage(str(cached), width=w * scale, height=h * scale)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(MID)
    canvas.line(18 * mm, 14 * mm, PAGE_W - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "Smart Voice Controlled Dustbin | Hardware Setup")
    canvas.drawRightString(PAGE_W - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="GuideTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=NAVY, spaceAfter=8))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["BodyText"], fontSize=12, leading=17, textColor=MUTED, spaceAfter=12))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=NAVY, spaceBefore=9, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=BLUE, spaceBefore=7, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=TEXT, spaceAfter=6))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED, spaceAfter=5))
styles.add(ParagraphStyle(name="Captionx", parent=styles["BodyText"], fontName="Helvetica-Oblique", fontSize=7.8, leading=10, alignment=TA_CENTER, textColor=MUTED, spaceBefore=3, spaceAfter=8))
styles.add(ParagraphStyle(name="Warningx", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9.3, leading=13, textColor=colors.HexColor("#8A2D1D"), spaceBefore=5, spaceAfter=7))
styles.add(ParagraphStyle(name="Bulletx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13, leftIndent=12, firstLineIndent=-7, bulletIndent=2, textColor=TEXT, spaceAfter=3))


def p(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def bullets(items):
    return [p(f"- {item}", "Bulletx") for item in items]


def table(rows, widths, header=True, font=8):
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#C9D3D9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
        for row in range(1, len(rows)):
            if row % 2 == 0:
                commands.append(("BACKGROUND", (0, row), (-1, row), PALE))
    t.setStyle(TableStyle(commands))
    return t


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=17 * mm, bottomMargin=19 * mm, title="Smart Voice Controlled Dustbin Hardware Setup Guide", author="Project documentation")
    doc.addPageTemplates(PageTemplate(id="main", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")], onPage=footer))

    story = [
        Spacer(1, 9 * mm),
        p("Smart Voice Controlled Dustbin", "GuideTitle"),
        p("Hardware Setup Guide", "Subtitle"),
        p("Wiring, power, VC-02 configuration, assembly, and bring-up for the ATmega328P-based prototype.", "Bodyx"),
        Spacer(1, 4 * mm),
        image("images/prototype.jpg", 174 * mm, 102 * mm),
        p("Prototype integration on the 4-wheel chassis during bench testing.", "Captionx"),
        p("Safety scope", "H2x"),
        p("This guide documents an educational prototype. It is not a certified medical device and must not be used for clinical waste without appropriate containment, cleaning, risk assessment, and regulatory approval.", "Warningx"),
        PageBreak(),
        p("1 System overview", "H1x"),
        p("The VC-02 recognizes configured speech offline and exposes the result as GPIO pulses or levels. The ATmega328P reads those lines, drives two motor channels, monitors the ultrasonic sensor in the current direction of travel, moves a lid servo only while stopped, and reports status on an I2C LCD."),
        p("Implemented behavior", "H2x"),
        *bullets([
            "Forward and backward commands are rising-edge pulse inputs.",
            "The active ultrasonic sensor stops motion at 20 cm or less.",
            "A maintained GPIO level opens the lid at HIGH and closes it at LOW.",
            "Motor PWM is fixed at 80 out of 255 in the supplied sketch.",
            "The system supports straight-line motion only; it does not steer or navigate autonomously.",
        ]),
        p("Signal flow", "H2x"),
        table([
            ["Source", "Signal", "Destination", "Effect"],
            ["VC-02 GPIO_B0", "200 ms pulse", "ATmega D8", "Start forward motion"],
            ["VC-02 GPIO_B1", "200 ms pulse", "ATmega D7", "Start backward motion"],
            ["VC-02 GPIO_A27", "HIGH / LOW", "ATmega D3", "Open / close lid"],
            ["Ultrasonic sensors", "Echo pulse", "ATmega D1 / D2", "Stop near obstacle"],
            ["ATmega328P", "PWM + direction", "Motor driver", "Drive the chassis"],
        ], [33 * mm, 31 * mm, 39 * mm, 67 * mm]),
        Spacer(1, 4 * mm),
        image("images/perfB.png", 128 * mm, 83 * mm),
        p("Early integration on perfboard and a dual-channel motor-driver module.", "Captionx"),
        PageBreak(),
        p("2 Parts and power", "H1x"),
        p("Core parts", "H2x"),
        table([
            ["Part", "Role", "Setup note"],
            ["ATmega328P", "Main controller", "Use a complete 16 MHz circuit or an Arduino Uno-compatible board."],
            ["AI-Thinker VC-02", "Offline voice recognition", "Flash the configured command model before system testing."],
            ["Dual H-bridge driver", "Motor direction and speed", "Size it for motor stall current; the photographed module is L298N-style."],
            ["2 x ultrasonic sensor", "Front and rear stopping", "Mount square to the direction of travel with a clear acoustic path."],
            ["16x2 I2C LCD", "Status display", "Firmware expects address 0x27 on A4/A5."],
            ["Servo", "Lid actuation", "Use a separate regulated rail if the servo causes resets."],
            ["Battery and regulators", "System power", "Choose ratings from measured motor stall and logic current."],
        ], [37 * mm, 48 * mm, 85 * mm], font=7.7),
        p("Power architecture", "H2x"),
        *bullets([
            "Feed the motors through the motor driver from a supply matched to the motors.",
            "Power the ATmega328P and LCD from a clean regulated logic rail.",
            "Power the VC-02 only at the voltage required by its exact carrier/module revision; verify its datasheet and board markings.",
            "A separate regulated servo rail is recommended. Join its ground to the controller ground.",
            "Connect every signal-source ground together: controller, VC-02, sensors, servo supply, and motor driver.",
            "Add a fuse near the battery, a master switch, and local decoupling. Keep motor wiring away from voice and sensor wiring.",
        ]),
        p("Do not power motors from the ATmega328P 5 V pin. Do not apply 5 V to a VC-02 GPIO unless that exact board is documented as 5 V tolerant.", "Warningx"),
        image("images/soldered work.jpg", 137 * mm, 88 * mm),
        p("Custom controller board with the VC-02 and ATmega328P during assembly.", "Captionx"),
        PageBreak(),
        p("3 Complete controller pin map", "H1x"),
        p("The mapping below is taken directly from <font name='Courier'>robot_controller.ino</font> and the supplied VC-02 pin note."),
        table([
            ["ATmega pin", "Connected device", "Device pin", "Direction / function"],
            ["D0 / RX", "Rear ultrasonic", "TRIG", "Output; used during backward motion"],
            ["D1 / TX", "Rear ultrasonic", "ECHO", "Input; used during backward motion"],
            ["D2", "Front ultrasonic", "ECHO", "Input; used during forward motion"],
            ["D3", "VC-02", "GPIO_A27", "Input; HIGH opens, LOW closes"],
            ["D5 (PWM)", "Motor driver", "ENA", "Motor A speed"],
            ["D6 (PWM)", "Motor driver", "ENB", "Motor B speed"],
            ["D7", "VC-02", "GPIO_B1", "Input; backward pulse"],
            ["D8", "VC-02", "GPIO_B0", "Input; forward pulse"],
            ["D9", "Servo", "Signal", "Output; lid angle"],
            ["D10", "Front ultrasonic", "TRIG", "Output; used during forward motion"],
            ["D11", "Motor driver", "IN1", "Motor A direction"],
            ["D12", "Motor driver", "IN2", "Motor A direction"],
            ["D13", "Motor driver", "IN3", "Motor B direction"],
            ["A0 / D14", "Motor driver", "IN4", "Motor B direction"],
            ["A4", "I2C LCD", "SDA", "I2C data"],
            ["A5", "I2C LCD", "SCL", "I2C clock"],
        ], [28 * mm, 47 * mm, 34 * mm, 61 * mm], font=7.25),
        p("Programming caution", "H2x"),
        p("D0 and D1 are the ATmega328P hardware UART pins. Their ultrasonic connections can interfere with bootloader uploads or serial debugging. Disconnect that sensor from D0/D1 while uploading if necessary. The current sketch does not use Serial, but future debugging will require relocating or isolating those signals.", "Warningx"),
        p("Motor outputs", "H2x"),
        p("Connect the left motor group to one H-bridge output and the right motor group to the other. If the platform rotates instead of traveling straight, reverse one channel's motor leads. Keep ENA and ENB jumpers removed when those pins are driven by D5 and D6 PWM."),
        PageBreak(),
        p("4 VC-02 configuration", "H1x"),
        p("Use the AI-Thinker voice platform linked in the repository note. Configure the three used outputs as shown below, generate the SDK/firmware, then flash the VC-02 using the vendor procedure for the exact module revision."),
        table([
            ["Behavior", "Recognized phrase examples", "Output setup"],
            ["collectTrash", "collect trash; come for trash; pick trash; come pick trash", "GPIO_B0; pulse; 200 ms; once"],
            ["takeTrash", "take trash; take trash now; take it back; take trash back", "GPIO_B1; pulse; 200 ms; once"],
            ["openCover", "open cover; open the trash cover; open for me; please open", "GPIO_A27; set HIGH"],
            ["closeCover", "close cover; close the trash cover; close for me; please close", "GPIO_A27; set LOW"],
        ], [29 * mm, 84 * mm, 57 * mm], font=7.6),
        Spacer(1, 4 * mm),
        image("images/control details.png", 174 * mm, 66 * mm),
        p("Supplied control-detail screen showing pulse and level actions.", "Captionx"),
        image("images/pin config.png", 158 * mm, 77 * mm),
        p("GPIO_B0, GPIO_B1, and GPIO_A27 selected in the voice-platform pin configuration.", "Captionx"),
        PageBreak(),
        p("5 Wiring and assembly sequence", "H1x"),
        Spacer(1, 2 * mm),
        p("1  Prepare the power system", "H2x"),
        p("With the battery disconnected, install the fuse and master switch. Verify the motor rail and regulated logic rails using a multimeter before connecting any module."),
        p("2  Wire the controller and display", "H2x"),
        p("Connect the ATmega328P support circuit and I2C LCD. Upload the sketch with D0/D1 loads disconnected. Confirm the display initializes at address 0x27 and shows the waiting message."),
        p("3  Connect the motor driver", "H2x"),
        p("Wire D5/D6 to ENA/ENB and D11/D12/D13/A0 to IN1-IN4. Connect each motor side to one output channel. Test with wheels lifted and use a current-limited supply."),
        p("4  Install ultrasonic sensors", "H2x"),
        p("Mount one sensor facing the rear and connect TRIG/ECHO to D0/D1. Mount the other facing forward and connect ECHO/TRIG to D2/D10. Power them from the logic rail and share ground."),
        p("5  Connect the servo", "H2x"),
        p("Connect the signal to D9. Before attaching the horn, power the controller once so the sketch commands 0 degrees; then fit the mechanism in the closed position without binding."),
        p("6  Connect the voice module", "H2x"),
        p("Connect GPIO_B0 to D8, GPIO_B1 to D7, and GPIO_A27 to D3. Add the common ground, then power the VC-02 from its verified rail. Keep voice wiring separated from the motor paths."),
        p("7  Secure and inspect", "H2x"),
        p("Strain-relieve battery and motor cables, insulate exposed conductors, check polarity, and confirm that no wiring can reach the wheels. The supplied STL enclosure can protect the custom control circuit after fit and temperature checks."),
        image("images/soldered side.jpg", 106 * mm, 81 * mm),
        p("Perfboard solder side. Inspect for bridges, cold joints, and insufficient clearance before power-up.", "Captionx"),
        PageBreak(),
        p("6 Bring-up and verification", "H1x"),
        p("Use this order to limit mechanical and electrical risk."),
        table([
            ["Step", "Test", "Expected result"],
            ["1", "Continuity and polarity with power off", "No short between rails; correct connector polarity"],
            ["2", "Logic-only power", "Stable regulated voltage; LCD shows waiting status"],
            ["3", "Motor test with chassis raised", "Both sides move forward and backward together"],
            ["4", "Front obstacle test", "Forward motion stops at about 20 cm"],
            ["5", "Rear obstacle test", "Backward motion stops at about 20 cm"],
            ["6", "Servo test while stopped", "Smooth travel between 0 and 90 degrees"],
            ["7", "Voice GPIO test", "Each configured phrase produces the intended action"],
            ["8", "Floor test at low risk", "Straight travel; no resets, overheating, or cable contact"],
        ], [14 * mm, 68 * mm, 88 * mm], font=7.7),
        p("Fault checks", "H2x"),
        table([
            ["Symptom", "Likely checks"],
            ["Upload fails", "Disconnect D0/D1 sensor; verify board, bootloader, serial adapter, and reset wiring."],
            ["LCD blank", "Confirm 0x27 address, SDA=A4, SCL=A5, contrast setting, 5 V, and ground."],
            ["Robot turns", "Reverse one motor channel or correct IN wiring; compare wheel direction with chassis raised."],
            ["Random resets", "Measure rail sag; separate servo/motor supply; add decoupling; improve grounding."],
            ["Does not stop", "Check TRIG/ECHO orientation and active sensor; test pulse timing and sensor field of view."],
            ["Voice action wrong", "Confirm GPIO_B0->D8, GPIO_B1->D7, GPIO_A27->D3 and regenerate VC-02 firmware."],
        ], [47 * mm, 123 * mm], font=7.8),
        p("Fail-safe limitation", "H2x"),
        p("If an ultrasonic echo times out, the supplied firmware returns -1 and continues motion because -1 is not treated as an obstacle. Keep the emergency power switch accessible and consider changing sensor faults to a stop condition before unattended testing.", "Warningx"),
        PageBreak(),
        p("7 Configuration reference", "H1x"),
        image("images/Basic information.png", 174 * mm, 48 * mm),
        p("Configured command vocabulary and spoken replies.", "Captionx"),
        image("images/control details edit.png", 174 * mm, 64 * mm),
        p("GPIO_B0 pulse action configured for the collectTrash behavior.", "Captionx"),
        image("images/sdk download.png", 174 * mm, 46 * mm),
        p("Voice-platform SDK generation and firmware download screen.", "Captionx"),
        p("Reference links", "H2x"),
        p("AI-Thinker configuration platform: https://voice.ai-thinker.com/<br/>Demonstration video: https://youtu.be/Hfe3AVP62qg"),
        p("Source of truth", "H2x"),
        p("Firmware behavior and controller assignments are defined in <font name='Courier'>robot_controller/robot_controller.ino</font>. The VC-02-to-controller mapping is recorded in <font name='Courier'>info.txt</font>. Rebuild this PDF with <font name='Courier'>scripts/build_hardware_guide.py</font> after changing either source."),
    ]
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
