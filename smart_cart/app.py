# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import cv2
import cv2.aruco as aruco
import numpy as np
import qrcode
import os
import time

app = Flask(__name__)

# CONFIGURATION
UPI_ID = "evinjoseph55-1@okhdfcbank"
PRODUCT_DB = {
    0: {"name": "Lays Chips", "price": 20},
    1: {"name": "Coca Cola", "price": 40},
    2: {"name": "Oreo Biscuits", "price": 30},
    3: {"name": "Maggi Noodles", "price": 15}
}

if not os.path.exists('static'):
    os.makedirs('static')

def run_vision_scanner(target_orders):
    # FIX 1: Change CAP_DSHOW to CAP_V4L2 for Linux
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2) 
    
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    
    fulfilled_counts = {pid: 0 for pid in target_orders.keys()}
    
    tracking_id = None
    stable_start_time = None
    REQUIRED_STABILITY = 2.0 
    waiting_for_removal = False 
    
    verified = False
    print("\n--- SCANNER STARTED: Point items at the HP Webcam ---")

    while True:
        ret, frame = cap.read()
        if not ret: 
            print("Failed to grab frame from camera. Check connection.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        # --- 1. CHECK IF MISSION ACCOMPLISHED ---
        all_done = True
        for pid in target_orders:
            if fulfilled_counts[pid] < target_orders[pid]:
                all_done = False
                break
                
        if all_done:
            print("\nSUCCESS: ALL ITEMS PICKED! Generating QR Code...")
            time.sleep(2) # Give a tiny pause before generating QR
            verified = True
            break

        # --- 2. VISION & COUNTING LOGIC ---
        visible_ids = []
        if ids is not None:
            visible_ids = ids.flatten().tolist()

        if waiting_for_removal:
            if tracking_id not in visible_ids:
                print(f"Item {PRODUCT_DB[tracking_id]['name']} removed. Ready for next.")
                waiting_for_removal = False
                tracking_id = None
        else:
            needed_visible = []
            for vid in visible_ids:
                if vid in target_orders and fulfilled_counts[vid] < target_orders[vid]:
                    needed_visible.append(vid)

            if needed_visible:
                target_to_scan = needed_visible[0] 
                
                if tracking_id != target_to_scan:
                    tracking_id = target_to_scan
                    stable_start_time = time.time()
                
                elapsed = time.time() - stable_start_time
                remaining = max(0, REQUIRED_STABILITY - elapsed)
                
                if remaining <= 0:
                    fulfilled_counts[tracking_id] += 1
                    p_name = PRODUCT_DB[tracking_id]["name"]
                    print(f"\n*** ADDED TO CART: {p_name} ({fulfilled_counts[tracking_id]}/{target_orders[tracking_id]}) ***")
                    waiting_for_removal = True 
                else:
                    p_name = PRODUCT_DB[tracking_id]["name"]
                    print(f"Scanning {p_name}... Hold still for {remaining:.1f}s", end='\r')
            else:
                tracking_id = None
                stable_start_time = None

    cap.release()
    return verified

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_scan', methods=['POST'])
def start_scan():
    order_cart = {}
    total_bill = 0
    
    for i in range(4):
        qty = int(request.form.get(f'qty_{i}', 0))
        if qty > 0:
            order_cart[i] = qty
            total_bill += (PRODUCT_DB[i]['price'] * qty)
    
    if not order_cart:
        return render_template('index.html')

    # Run Vision
    success = run_vision_scanner(order_cart)
    
    if success:
        # Generate QR
        upi_link = f"upi://pay?pa={UPI_ID}&pn=SmartCart&am={total_bill}&cu=INR"
        qr = qrcode.make(upi_link)
        qr_path = "static/payment_qr.png"
        qr.save(qr_path)
        return render_template('index.html', qr_image=qr_path, total_amount=total_bill)
    else:
        return "<h1>Scan Cancelled. <a href='/'>Try Again</a></h1>"

if __name__ == '__main__':
    # FIX 3: Bind to 0.0.0.0 so you can access it via the Pi's IP address on your network
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)