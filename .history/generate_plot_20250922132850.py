import fastf1
import fastf1.plotting as f1plt
import matplotlib.pyplot as plt

# Cache to speed up future runs
fastf1.Cache.enable_cache(".fastf1")

# Pick a session (year, round number or GP name, session code)
session = fastf1.get_session(2025, "Baku", "R")   
session.load(laps=True, telemetry=True)      # first time will download data

# Fastest lap overall
lap = session.laps.pick_driver("VER")
tel = lap.get_telemetry()  # has Distance, Speed, Throttle, Brake, etc.

# Nice default style
f1plt.setup_mpl()

fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
ax.plot(tel["Distance"], tel["Speed"])
ax.set_xlabel("Distance [m]")
ax.set_ylabel("Speed [km/h]")
ax.set_title(f"{session.event['EventName']} {session.event.year} — {session.name}\n"
             f"Fastest: {lap['Driver']}  Time: {lap['LapTime']}")
ax.grid(True)

fig.tight_layout()
fig.savefig("plot.png", bbox_inches="tight")
print("Saved plot.png")
