# ⚡ Power Setup

### Overview
This section covers how to properly wire and power the servos and control system for the Robot Hand.  
You’ll be connecting your 5 V power supply, distributing current through 18 AWG wiring, and soldering the servo power, ground, and signal leads to their respective connections on the ESP32 board.

---

### Materials Needed
- 18 AWG silicone wire (red for power, black for ground)
- 5 V ≥ 5 A power source  
- 5 × SG90 servo motors  
- Soldering iron and solder  
- Wire cutters and strippers  
- Heat-shrink tubing or electrical tape  

---

### 1. Prepare the Power Leads
1. Cut two lengths of **18 AWG wire** — one for **power (red)** and one for **ground (black)**.  
2. **Solder these wires directly to your power source**, connecting:  
   - Red → **5 V output**  
   - Black → **Ground (GND)**  
3. Ensure your joints are solid and insulated properly.

---

### 2. Prepare the Servo Wires
1. Cut off the **female connectors** from each servo cable.  
2. Separate the three wires in each servo cable:
   - **Red** → Power  
   - **Brown or Black** → Ground  
   - **Yellow or Orange** → Signal  
3. Strip a small section of insulation off each end for soldering.

---

### 3. Power Distribution
1. Solder all **servo red wires** to the **18 AWG power line**.  
2. Solder all **servo brown/black wires** to the **18 AWG ground line**.  
3. **Add one extra wire from the 18 AWG ground line** and solder its other end to a **GND pin on the Arduino/ESP32**.  
   - This connects the Arduino ground to the servo ground, ensuring all components share a **common electrical reference**.  
4. Double-check polarity before applying power — reversing power and ground will damage servos.  
5. Optionally, apply heat-shrink tubing over each joint for safety and durability.

---

### 4. Signal Wiring and Routing
1. Route all **servo signal wires (yellow)** through the **hole on the back of the wrist**, leading into the **large wrist cavity** where the Arduino/ESP32 is mounted.  
2. Once the wires reach the control board area, solder each **signal wire** to the corresponding **GPIO pin**:

| Servo | GPIO Pin |
|--------|-----------|
| Pinky | GPIO 27 |
| Ring | GPIO 26 |
| Middle | GPIO 25 |
| Index | GPIO 33 |
| Thumb | GPIO 32 |

3. Keep wires tidy and ensure no bare connections are exposed.

---

### 5. Verification
- Before powering on, confirm:
  - 5 V and GND are consistent across all servos.  
  - The **Arduino ground** is properly connected to the shared ground line.  
  - Signal wires are connected to the correct pins.  
  - No short circuits between power and ground.  
- Power up the system and gently test each servo to ensure movement.

---

**Tip:** If the servos jitter or reset, your power source may be under-rated. Each servo can draw up to **1 A under load**, so aim for **at least 5 A continuous current** capability.
