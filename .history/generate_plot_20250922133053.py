import fastf1
import fastf1.plotting as f1plt
import matplotlib.pyplot as plt

# Cache to speed up future runs
fastf1.Cache.enable_cache(".fastf1")

# Pick a session (year, round number or GP name, session code)
session = fastf1.get_session(2025, "Baku", "R")   
session.load(laps=True, telemetry=True)      # first time will download data

# Fastest lap overall
lap1 = session.laps.pick_driver("VER").pick_fastest()
lap2  = session.laps.pick_driver("LEC").pick_fastest()
tel1, tel2 = lap1.get_telemetry(), lap2.get_telemetry()  # has Distance, Speed, Throttle, Brake, etc.

# Nice default style
f1plt.setup_mpl()

fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
ax.plot(tel1["Distance"], tel1["Speed"], label="VER")
ax.plot(tel2["Distance"], tel2["Speed"], label="LEC")
ax.set_xlabel("Distance [m]")
ax.set_ylabel("Speed [km/h]")
ax.set_title(f"{session.event['EventName']} {session.event.year} — {session.name}\n"
             f"Fastest: {lap1['Driver']}  Time: {lap1['LapTime']}")
ax.grid(True)

fig.tight_layout()
fig.savefig("plot.png", bbox_inches="tight")
print("Saved plot.png")
