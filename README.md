# 🔐 SmartCard Security Project – TUM SmartCard Lab

This repository documents the implementation and evaluation of secure SmartCard communication, conducted as part of the **SmartCard Lab** at the **Technical University of Munich (TUM)**. The project was completed in collaboration with Sevan and focused on analyzing protocol-level vulnerabilities and reinforcing the system against physical and logical attacks.

---

## 🧩 Part 1 – Communication Setup & Protocol Analysis

The first phase focused on establishing a working SmartCard communication stack based on **ISO/IEC 7816-3** and the **T=0 protocol**. This involved building the foundational firmware and host interface to support structured data exchange between a terminal and the SmartCard.

### 🔧 Key Components:
- **USART initialization** for ISO 7816-3-compliant asynchronous communication
- Implementation of the **T=0 character-level protocol**
- Handling of **APDU command parsing and response formatting**
- Logging and visualization of command exchanges using logic analyzers

### 🛠️ Tools & Technologies:
- STM32 microcontroller (ARM Cortex-M)
- Low-level C firmware
- Hardware debugging tools (logic analyzer, serial monitor)

---

## 🎯 Part 2 – Side-Channel Attack & Countermeasures

In the second phase, the focus shifted to **security evaluation** through **Differential Power Analysis (DPA)** and **countermeasure implementation**.

### 🧪 Attack Execution:
- Collected power traces during AES execution
- Analyzed data leakage patterns from intermediate rounds
- Demonstrated potential key recovery under unprotected conditions

### 🔐 Hardening Techniques:
- Introduced **masking** and **shuffling** countermeasures in AES S-box operations
- Measured and compared power trace uniformity before and after protection
- Evaluated the performance-security trade-off of implemented defenses



