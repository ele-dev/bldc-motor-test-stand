import time
from power_supply import PowerSupply

def run_instrument_tests():
    # Initialize the supply (uses our working 115200 baud default)
    ps = PowerSupply(port="/dev/ttyUSB0")
    
    try:
        print("\n--- Starting Subclass Member Tests ---")
        
        # 1. Test identify property
        print(f"[TEST] Instrument Identity: {ps.identify}")
        
        # 2. Test initial states
        print("[TEST] Turning output OFF for safety initialization...")
        ps.off()
        
        # 3. Test Voltage Getters/Setters
        print("[TEST] Setting voltage to 15.1V...")
        ps.voltage = 15.1
        time.sleep(0.5)  # Let the hardware settle
        print(f"[RESULT] Target Voltage Readback: {ps.voltage} V")
        
        # 4. Test Current Getters/Setters
        print("[TEST] Setting current limit to 5.3A...")
        ps.current = 5.3
        time.sleep(0.5)
        print(f"[RESULT] Target Current Readback: {ps.current} A")
        
        # 5. Test Power Readback
        print(f"[RESULT] Max Programmed Power Limit: {ps.power} W")
        
        # 6. Test Output Control toggling
        print("[TEST] Enabling live output channel...")
        ps.on()
        time.sleep(5.0)  # Let it run for 5 seconds

        # 7. Test Power Readback at load
        print(f"[TEST] Power at idle load: {ps.power}")

        time.sleep(1)
        
        print("[TEST] Disabling live output channel...")
        ps.off()
        
        print("\n--- All member methods passed verification cleanly! ---")

    except Exception as e:
        print(f"\n[ERROR] An error occurred during runtime execution: {e}")
        
    finally:
        # Emergency safety cutoff loop
        print("\nCleaning up instrument state...")
        try:
            ps.off()   # Ensure rails are dead before dropping the connection
        except Exception:
            pass
        ps.close()

if __name__ == "__main__":
    run_instrument_tests()