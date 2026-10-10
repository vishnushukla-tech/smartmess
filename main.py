from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict
from datetime import datetime

app = FastAPI()

# Secured Admin Key
ADMIN_PASSWORD = "smartmess_ugi.vs"

# Roll_no -> dict of meals
daily_records: Dict[str, dict] = {}

class MealSelection(BaseModel):
    roll_no: str
    name: str
    breakfast: bool
    lunch: bool
    snacks: bool
    dinner: bool

class AdminAction(BaseModel):
    pin: str

@app.post("/api/submit")
def submit_status(data: MealSelection):
    clean_roll = data.roll_no.strip().upper()
    daily_records[clean_roll] = {
        "name": data.name.strip(),
        "breakfast": data.breakfast,
        "lunch": data.lunch,
        "snacks": data.snacks,
        "dinner": data.dinner,
        "timestamp": datetime.now().strftime("%I:%M %p")
    }
    return {"message": "Attendance registered successfully", "total": len(daily_records)}

@app.post("/api/summary")
def get_summary(auth: AdminAction):
    if auth.pin != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized Admin Password")
    
    b_count = sum(1 for s in daily_records.values() if s.get("breakfast"))
    l_count = sum(1 for s in daily_records.values() if s.get("lunch"))
    s_count = sum(1 for s in daily_records.values() if s.get("snacks"))
    d_count = sum(1 for s in daily_records.values() if s.get("dinner"))
    
    return {
        "total_responses": len(daily_records),
        "breakfast": b_count,
        "lunch": l_count,
        "snacks": s_count,
        "dinner": d_count,
        "student_list": daily_records
    }

@app.post("/api/reset-today")
def reset_today(auth: AdminAction):
    if auth.pin != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized Admin Password")
    daily_records.clear()
    return {"message": "All records cleared successfully"}

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>SmartMess Platform</title>
      <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { margin: 0; background: #f8fafc; color: #1e293b; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 25px; }
        .status-pill { display: inline-block; background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 999px; font-size: 13px; font-weight: 600; }
        .tabs { display: flex; gap: 10px; justify-content: center; margin-bottom: 25px; }
        .tab-btn { padding: 10px 24px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; background: #cbd5e1; color: #334155; }
        .tab-btn.active { background: #0284c7; color: white; }
        .panel { display: none; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .panel.active { display: block; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 14px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 15px; }
        .meal-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin: 20px 0; }
        .meal-card { display: flex; align-items: center; gap: 10px; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc; font-weight: 500; cursor: pointer; }
        .submit-btn { width: 100%; padding: 12px; background: #0284c7; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .submit-btn:hover { background: #0369a1; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
        .stat-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; }
        .stat-box h4 { margin: 0 0 8px 0; font-size: 13px; color: #64748b; text-transform: uppercase; }
        .stat-box p { margin: 0; font-size: 28px; font-weight: 700; color: #0284c7; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }
        th, td { border: 1px solid #e2e8f0; padding: 10px; text-align: left; }
        th { background: #f8fafc; color: #475569; }
        .badge-in { color: #16a34a; font-weight: 700; background: #dcfce7; padding: 3px 8px; border-radius: 4px; }
        .badge-out { color: #dc2626; font-weight: 700; background: #fee2e2; padding: 3px 8px; border-radius: 4px; }
        #status-msg { margin-top: 15px; text-align: center; font-weight: 600; }
        .admin-lock-card { text-align: center; padding: 40px 20px; }
      </style>
    </head>
    <body>
      <div class="container">
        <header>
          <h1 style="margin-bottom: 4px;">SmartMess</h1>
          <p style="color: #64748b; margin: 0 0 8px 0;">Automated Kitchen Headcount Platform</p>
          <span class="status-pill" id="poll-indicator">● System Live</span>
        </header>

        <div class="tabs">
          <button class="tab-btn active" onclick="switchTab('student')">Student Portal</button>
          <button class="tab-btn" onclick="switchTab('kitchen')">Kitchen Display (Admin)</button>
        </div>

        <!-- Student Portal -->
        <div id="student" class="panel active">
          <h2 style="margin-top:0;">Daily Meal Check-in</h2>
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" id="name" placeholder="e.g. Rahul Sharma" />
          </div>
          <div class="form-group">
            <label>Roll Number / Hostel ID</label>
            <input type="text" id="roll" placeholder="e.g. CS-101" />
          </div>

          <label>Select meals you plan to eat:</label>
          <div class="meal-row">
            <label class="meal-card"><input type="checkbox" id="b" checked /> Breakfast</label>
            <label class="meal-card"><input type="checkbox" id="l" checked /> Lunch</label>
            <label class="meal-card"><input type="checkbox" id="s" checked /> Evening Snacks</label>
            <label class="meal-card"><input type="checkbox" id="d" checked /> Dinner</label>
          </div>

          <button class="submit-btn" id="sub-btn" onclick="submitAttendance()">Submit Attendance</button>
          <div id="status-msg"></div>
        </div>

        <!-- Kitchen Portal -->
        <div id="kitchen" class="panel">
          <!-- Password Lock -->
          <div id="admin-login" class="admin-lock-card">
            <h3>🔒 Kitchen Admin Login</h3>
            <p style="color: #64748b; font-size: 14px;">Enter Authorized Password to view live headcount</p>
            <input type="password" id="admin-pin-input" placeholder="Enter Admin Password" style="max-width: 280px; text-align: center; margin-bottom: 12px;" />
            <br />
            <button class="submit-btn" style="max-width: 280px;" onclick="unlockAdmin()">Unlock Display</button>
            <div id="login-err" style="color: #dc2626; margin-top: 10px; font-weight: 600;"></div>
          </div>

          <!-- Live Display -->
          <div id="admin-content" style="display: none;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
              <div>
                <h2 style="margin:0;">Live Kitchen Prep Count</h2>
                <small style="color: #16a34a; font-weight:600;">● Auto-syncing live every 3s</small>
              </div>
              <div style="display:flex; gap:8px;">
                <button onclick="loadKitchenData()" style="padding:6px 12px; border-radius:6px; cursor:pointer;">Refresh</button>
                <button onclick="resetTodayData()" style="padding:6px 12px; border-radius:6px; cursor:pointer; background:#fee2e2; color:#b91c1c; border:1px solid #fecaca;">Clear All</button>
                <button onclick="lockAdmin()" style="padding:6px 12px; border-radius:6px; cursor:pointer; background:#f1f5f9;">Lock</button>
              </div>
            </div>

            <div class="stats-grid">
              <div class="stat-box"><h4>Breakfast</h4><p id="cnt-b">0</p></div>
              <div class="stat-box"><h4>Lunch</h4><p id="cnt-l">0</p></div>
              <div class="stat-box"><h4>Snacks</h4><p id="cnt-s">0</p></div>
              <div class="stat-box"><h4>Dinner</h4><p id="cnt-d">0</p></div>
            </div>

            <h3>Student Roster (<span id="total-students">0</span> responses)</h3>
            <table>
              <thead>
                <tr>
                  <th>Roll No</th>
                  <th>Name</th>
                  <th>Breakfast</th>
                  <th>Lunch</th>
                  <th>Snacks</th>
                  <th>Dinner</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody id="student-table-body">
                <tr><td colspan="7" style="text-align:center;">No submissions recorded yet.</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <script>
        let currentAdminPass = "";
        let pollTimer = null;

        function switchTab(tabId) {
          document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
          document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
          if (tabId === 'student') {
            document.querySelectorAll('.tab-btn')[0].classList.add('active');
            document.getElementById('student').classList.add('active');
            stopAutoRefresh();
          } else {
            document.querySelectorAll('.tab-btn')[1].classList.add('active');
            document.getElementById('kitchen').classList.add('active');
            if (currentAdminPass) {
              loadKitchenData();
              startAutoRefresh();
            }
          }
        }

        async function submitAttendance() {
          const name = document.getElementById('name').value.trim();
          const roll = document.getElementById('roll').value.trim();
          const msg = document.getElementById('status-msg');
          const btn = document.getElementById('sub-btn');

          if (!name || !roll) {
            msg.innerText = "Please enter both Name and Roll Number.";
            msg.style.color = "#dc2626";
            return;
          }

          btn.disabled = true;
          btn.innerText = "Submitting...";

          const payload = {
            roll_no: roll,
            name: name,
            breakfast: document.getElementById('b').checked,
            lunch: document.getElementById('l').checked,
            snacks: document.getElementById('s').checked,
            dinner: document.getElementById('d').checked
          };

          try {
            const res = await fetch('/api/submit', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
            });

            if (res.ok) {
              msg.innerText = "Attendance submitted successfully! The kitchen dashboard has updated.";
              msg.style.color = "#16a34a";
            } else {
              msg.innerText = "Server rejected the submission.";
              msg.style.color = "#dc2626";
            }
          } catch(e) {
            msg.innerText = "Connection error. Please try again.";
            msg.style.color = "#dc2626";
          } finally {
            btn.disabled = false;
            btn.innerText = "Submit Attendance";
          }
        }

        async function unlockAdmin() {
          const pass = document.getElementById('admin-pin-input').value.trim();
          const err = document.getElementById('login-err');
          
          try {
            const res = await fetch('/api/summary', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ pin: pass })
            });

            if (!res.ok) {
              err.innerText = "Incorrect Password. Access denied.";
              return;
            }

            const data = await res.json();
            currentAdminPass = pass;
            err.innerText = "";
            document.getElementById('admin-login').style.display = "none";
            document.getElementById('admin-content').style.display = "block";
            renderDashboard(data);
            startAutoRefresh();
          } catch(e) {
            err.innerText = "Network error connecting to backend.";
          }
        }

        function startAutoRefresh() {
          stopAutoRefresh();
          pollTimer = setInterval(loadKitchenData, 3000);
        }

        function stopAutoRefresh() {
          if (pollTimer) clearInterval(pollTimer);
        }

        function lockAdmin() {
          stopAutoRefresh();
          currentAdminPass = "";
          document.getElementById('admin-pin-input').value = "";
          document.getElementById('admin-login').style.display = "block";
          document.getElementById('admin-content').style.display = "none";
        }

        async function loadKitchenData() {
          if (!currentAdminPass) return;
          try {
            const res = await fetch('/api/summary', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ pin: currentAdminPass })
            });
            if (res.ok) {
              const data = await res.json();
              renderDashboard(data);
            }
          } catch(e) {
            console.error("Auto-sync error", e);
          }
        }

        function renderDashboard(data) {
          document.getElementById('cnt-b').innerText = data.breakfast;
          document.getElementById('cnt-l').innerText = data.lunch;
          document.getElementById('cnt-s').innerText = data.snacks;
          document.getElementById('cnt-d').innerText = data.dinner;
          document.getElementById('total-students').innerText = data.total_responses;

          const tbody = document.getElementById('student-table-body');
          const students = Object.entries(data.student_list);

          if (students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No submissions recorded yet.</td></tr>';
            return;
          }

          tbody.innerHTML = '';
          students.forEach(([roll, info]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td><strong>${roll}</strong></td>
              <td>${info.name}</td>
              <td><span class="${info.breakfast ? 'badge-in' : 'badge-out'}">${info.breakfast ? 'IN' : 'OUT'}</span></td>
              <td><span class="${info.lunch ? 'badge-in' : 'badge-out'}">${info.lunch ? 'IN' : 'OUT'}</span></td>
              <td><span class="${info.snacks ? 'badge-in' : 'badge-out'}">${info.snacks ? 'IN' : 'OUT'}</span></td>
              <td><span class="${info.dinner ? 'badge-in' : 'badge-out'}">${info.dinner ? 'IN' : 'OUT'}</span></td>
              <td style="color:#64748b; font-size:12px;">${info.timestamp || ''}</td>
            `;
            tbody.appendChild(row);
          });
        }

        async function resetTodayData() {
          if (!currentAdminPass) return;
          if (!confirm("Are you sure you want to clear all records?")) return;

          const res = await fetch('/api/reset-today', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pin: currentAdminPass })
          });

          if (res.ok) {
            loadKitchenData();
          }
        }
      </script>
    </body>
    </html>
    """
