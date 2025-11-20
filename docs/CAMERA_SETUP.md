# Camera Setup Guide - Tuya/ICSee Cameras

**Project:** Raspberry Pi Smart Monitoring Kit  
**Issue:** Camera does NOT support RTSP/ONVIF officially  
**Solution:** Use HTTP MJPEG or Snapshot API

---

## Camera Information

**Manufacturer Confirmation:**
- This camera model does NOT support RTSP/ONVIF officially
- Common in Tuya/ICSee/ImCam Pro cameras
- Alternative methods available

---

## Supported Camera Access Methods

### Option 1: HTTP MJPEG Stream (Recommended) ⭐

**Description:** Continuous video stream via HTTP MJPEG protocol

**Common URLs for Tuya/ICSee Cameras:**
```
http://CAMERA_IP:88/cgi-bin/mjpg/video.cgi
http://CAMERA_IP/video/mjpeg.cgi
http://CAMERA_IP/cgi-bin/mjpeg?channel=0
```

**Configuration (.env file):**
```bash
CAMERA_TYPE=mjpeg
CAMERA_MJPEG_URL=http://192.168.1.100:88/cgi-bin/mjpg/video.cgi
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your_password
```

**Advantages:**
- ✅ Continuous video stream
- ✅ Low latency
- ✅ Works with most Tuya/ICSee cameras
- ✅ Compatible with OpenCV

**Disadvantages:**
- ⚠️ Higher bandwidth usage
- ⚠️ May require authentication

---

### Option 2: HTTP Snapshot API

**Description:** Periodic image capture via HTTP snapshot endpoint

**Common URLs for Tuya/ICSee Cameras:**
```
http://CAMERA_IP:88/cgi-bin/snapshot.cgi?channel=0
http://CAMERA_IP/cgi-bin/snapshot.cgi
http://CAMERA_IP/tmpfs/auto.jpg
http://CAMERA_IP/snapshot.jpg
```

**Configuration (.env file):**
```bash
CAMERA_TYPE=snapshot
CAMERA_SNAPSHOT_URL=http://192.168.1.100:88/cgi-bin/snapshot.cgi?channel=0
CAMERA_SNAPSHOT_INTERVAL=0.5
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your_password
```

**Advantages:**
- ✅ Lower bandwidth usage
- ✅ Simple implementation
- ✅ Works with most IP cameras

**Disadvantages:**
- ⚠️ Not continuous (periodic snapshots)
- ⚠️ Higher latency
- ⚠️ May miss fast motion

---

### Option 3: USB Capture Card (Fallback)

**Description:** Use USB video capture device to convert camera output

**Hardware Required:**
- USB Video Capture Card (e.g., EasyCap, HDMI to USB)
- Connect camera's video output to USB capture card
- Connect USB capture card to Raspberry Pi

**Configuration (.env file):**
```bash
CAMERA_TYPE=usb
CAMERA_USB_DEVICE=/dev/video0
CAMERA_USB_INDEX=0
```

**Advantages:**
- ✅ Works with ANY camera (even analog)
- ✅ No network dependency
- ✅ Reliable connection
- ✅ Low latency

**Disadvantages:**
- ⚠️ Requires additional hardware (~$10-20)
- ⚠️ Physical connection needed
- ⚠️ Limited by USB bandwidth

---

## Testing Camera URLs

### Method 1: Browser Test
```
1. Open browser
2. Navigate to: http://CAMERA_IP:88/cgi-bin/mjpg/video.cgi
3. Enter username/password if prompted
4. Check if video stream appears
```

### Method 2: curl Test
```bash
# Test snapshot
curl -u admin:password http://CAMERA_IP:88/cgi-bin/snapshot.cgi?channel=0 -o test.jpg

# Test MJPEG stream
curl -u admin:password http://CAMERA_IP:88/cgi-bin/mjpg/video.cgi
```

### Method 3: VLC Test
```
1. Open VLC Media Player
2. Media → Open Network Stream
3. Enter: http://admin:password@CAMERA_IP:88/cgi-bin/mjpg/video.cgi
4. Click Play
```

### Method 4: Python Test
```python
import cv2

# Test MJPEG
url = "http://admin:password@192.168.1.100:88/cgi-bin/mjpg/video.cgi"
cap = cv2.VideoCapture(url)
ret, frame = cap.read()
if ret:
    print("✅ MJPEG stream working!")
    cv2.imwrite("test_frame.jpg", frame)
else:
    print("❌ MJPEG stream failed")
cap.release()
```

---

## Common Tuya/ICSee Camera URLs

Try these URLs with your camera IP:

### MJPEG Streams:
```
http://CAMERA_IP:88/cgi-bin/mjpg/video.cgi
http://CAMERA_IP/video/mjpeg.cgi
http://CAMERA_IP/cgi-bin/mjpeg?channel=0
http://CAMERA_IP:8080/video
```

### Snapshot URLs:
```
http://CAMERA_IP:88/cgi-bin/snapshot.cgi?channel=0
http://CAMERA_IP/cgi-bin/snapshot.cgi
http://CAMERA_IP/tmpfs/auto.jpg
http://CAMERA_IP/snapshot.jpg
http://CAMERA_IP/image/jpeg.cgi
```

### Common Ports:
- Port 88 (most common for Tuya/ICSee)
- Port 80 (standard HTTP)
- Port 8080 (alternative HTTP)
- Port 554 (RTSP - not supported by this camera)

---

## Troubleshooting

### Issue: "Connection Refused"
**Solution:**
- Check camera IP address
- Verify camera is on same network
- Try different ports (88, 80, 8080)
- Check firewall settings

### Issue: "401 Unauthorized"
**Solution:**
- Verify username/password
- Check camera admin credentials
- Try default credentials (admin/admin, admin/123456)

### Issue: "404 Not Found"
**Solution:**
- Try different URL patterns listed above
- Check camera manufacturer documentation
- Use network scanner to find open ports

### Issue: "Stream Timeout"
**Solution:**
- Increase timeout in code
- Check network stability
- Try lower resolution stream
- Use snapshot method instead

---

## Recommended Approach

**For Yoshinori's Camera:**

1. **First, try MJPEG streams** (best for continuous monitoring):
   ```
   http://CAMERA_IP:88/cgi-bin/mjpg/video.cgi
   http://CAMERA_IP/video/mjpeg.cgi
   ```

2. **If MJPEG fails, try snapshot API**:
   ```
   http://CAMERA_IP:88/cgi-bin/snapshot.cgi?channel=0
   ```

3. **If both fail, use USB capture card** (most reliable fallback)

---

## Next Steps

1. **Get camera IP address** from Yoshinori
2. **Test all URL patterns** with camera
3. **Update .env file** with working URL
4. **Test with Python script**
5. **Integrate with RTSP handler** (will be updated to support MJPEG/Snapshot)

---

**Developer:** Abdul Raheem Ansari  
**Email:** ansarirahim1@gmail.com  
**WhatsApp:** +91 9024304883  
**Date:** November 20, 2025

