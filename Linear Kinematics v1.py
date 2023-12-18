import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import os
from reportlab.lib.utils import ImageReader

#import kinovea csvs and edit column names

HeadX = pd.read_csv("D:\\yolov8-gpu\\runs\\pose\\predict4\\head_x_disp.csv")
ToeY = pd.read_csv("D:\\yolov8-gpu\\runs\\pose\\predict4\\toe_y_disp.csv")
HeadX = HeadX.rename(columns={'Trajectory 1': 'Trajectory', 'Time (ms)': 'Time'})
ToeY = ToeY.rename(columns={'Trajectory 2': 'Trajectory', 'Time (ms)': 'Time'})

#convert ms to s
HeadX['Time'] = (HeadX['Time'] / 1000)
ToeY['Time'] = (ToeY['Time'] / 1000)

#trial is left to right, so values are in the neg direction. *-1 to rectify
HeadX['Trajectory'] = HeadX['Trajectory'] * -1

#calc velocity from dispalacement and time
def calc_velocity(row):
    if row['Time']  !=0:
        return row['Trajectory']/ row['Time']
    else:
        return 0

#create new vel column in DF

HeadX['Velocity'] = HeadX.apply(lambda row: calc_velocity(row), axis=1)
ToeY['Velocity'] = ToeY.apply(lambda row: calc_velocity(row), axis=1)

#define toe data
time = ToeY['Time']
displacement = ToeY['Trajectory']

#find peaks and valleys in YToeDisp
peaks = find_peaks(displacement)[0]
neg_peaks = find_peaks(-displacement)[0]

#calc number of UDK defined as number of downkicks, and associated timestamps

num_UDK = len(peaks)
UDK_timestamps = ToeY.loc[neg_peaks, 'Time']
UDKTS = pd.Series(UDK_timestamps)
UDKTS = UDKTS.reset_index(drop=True)

# Plot the displacement data with identified peaks/valleys
plt.figure(figsize=(10, 6))
plt.plot(time, displacement, label='Displacement')
plt.plot(time[peaks], displacement[peaks], 'rx', label='Peaks')
plt.plot(time[neg_peaks], displacement[neg_peaks], 'go', label='Valleys')
plt.title(f'Displacement Data with {num_UDK} UDK')
plt.xlabel('Time')
plt.ylabel('Displacement')
plt.legend()


#calc tempo per kick
UDK_tempo = np.diff(time[neg_peaks])

#calc HeadX at each ToeY valley
HeadXatDownkicks = HeadX.iloc[neg_peaks]

#find disp of each up and downkick
peak_disp = ToeY['Trajectory'].iloc[peaks]
neg_peak_disp = ToeY['Trajectory'].iloc[neg_peaks]
KickDisp = pd.DataFrame({'Upkick Disp':peak_disp, 'Downkick Disp': neg_peak_disp})
KickDisp = KickDisp.reset_index()
KickDisp = KickDisp.drop('index', axis=1)
KickDisp = KickDisp * -1

#calc displacement of upkick and downkick, plus symmetry
AmpCalcs = pd.DataFrame(index=range(1, num_UDK+1))
AmpCalcs.loc[1, 'Upkick'] = KickDisp.loc[0, 'Downkick Disp'] - KickDisp.loc[1, 'Upkick Disp']
AmpCalcs.loc[1, 'Downkick'] = KickDisp.loc[2, 'Downkick Disp'] - KickDisp.loc[1, 'Upkick Disp']
AmpCalcs.loc[2, 'Upkick'] = KickDisp.loc[2, 'Downkick Disp'] - KickDisp.loc[3, 'Upkick Disp']
AmpCalcs.loc[2, 'Downkick'] = KickDisp.loc[4, 'Downkick Disp'] - KickDisp.loc[3, 'Upkick Disp']
AmpCalcs.loc[3, 'Upkick'] = KickDisp.loc[4, 'Downkick Disp'] - KickDisp.loc[5, 'Upkick Disp']
AmpCalcs.loc[3, 'Downkick'] = KickDisp.loc[6, 'Downkick Disp'] - KickDisp.loc[5, 'Upkick Disp']
AmpCalcs.loc[4, 'Upkick'] = KickDisp.loc[6, 'Downkick Disp'] - KickDisp.loc[7, 'Upkick Disp']
AmpCalcs.loc[4, 'Downkick'] = KickDisp.loc[8, 'Downkick Disp'] - KickDisp.loc[7, 'Upkick Disp']
AmpCalcs.loc[5, 'Upkick'] = KickDisp.loc[8, 'Downkick Disp'] - KickDisp.loc[9, 'Upkick Disp']
AmpCalcs.loc[5, 'Downkick'] = KickDisp.loc[10, 'Downkick Disp'] - KickDisp.loc[9, 'Upkick Disp']
AmpCalcs.loc[6, 'Upkick'] = KickDisp.loc[10, 'Downkick Disp'] - KickDisp.loc[11, 'Upkick Disp']
AmpCalcs.loc[6, 'Downkick'] = KickDisp.loc[12, 'Downkick Disp'] - KickDisp.loc[11, 'Upkick Disp']
AmpCalcs.loc[7, 'Upkick'] = KickDisp.loc[12, 'Downkick Disp'] - KickDisp.loc[13, 'Upkick Disp']
AmpCalcs.loc[7, 'Downkick'] = KickDisp.loc[14, 'Downkick Disp'] - KickDisp.loc[13, 'Upkick Disp']
AmpCalcs['Symmetry'] = (AmpCalcs['Upkick'] / AmpCalcs['Downkick']) *100
AmpCalcs['AvgAmp'] = (AmpCalcs['Upkick'] + AmpCalcs['Downkick']) / 2


#create refined data dashboard with
#UDK #, Time, Y Pos of downkick, X pos of head @ previous timestamp, tempo of kick, vel of kick, and amp of kick
Dashboard = pd.DataFrame(index=range(1, num_UDK+1))
Dashboard['UDK #'] = range(1, num_UDK+1)
Dashboard['Tempo'] = UDK_tempo
Dashboard['Amplitude'] = AmpCalcs['AvgAmp']
Dashboard['Symmetry'] = AmpCalcs['Symmetry']


print(KickDisp)

#create velocity graph
plt.figure(figsize=(6,2))
plt.plot(HeadX['Time'], HeadX['Velocity'], marker='o', linestyle='-')
plt.xlabel('UDK #')
plt.ylabel('Velocity (m/s)')
plt.title('X Velocity (m/s)')
plt.ylim(0,2)

vel_graph = BytesIO()
plt.savefig(vel_graph, format='png')
vel_graph.seek(0)
plt.close()
vel_graph_reader = ImageReader(vel_graph)

#create Tempo graph
plt.figure(figsize=(4,2))
plt.plot(Dashboard['UDK #'], Dashboard['Tempo'], marker='o', linestyle='-')
plt.xlabel('UDK #')
plt.ylabel('Tempo (sec)')
plt.title('Tempo (sec)')
plt.ylim(0,1)

tempo_graph = BytesIO()
plt.savefig(tempo_graph, format='png')
tempo_graph.seek(0)
plt.close()
tempo_graph_reader = ImageReader(tempo_graph)

#create amplitude graph
plt.figure(figsize=(4,2))
plt.plot(Dashboard['UDK #'], Dashboard['Amplitude'], marker='o', linestyle='-')
plt.xlabel('UDK #')
plt.ylabel('Amplitude (m)')
plt.title('Amplitude (m)')
plt.ylim(0,1)

amp_graph = BytesIO()
plt.savefig(amp_graph, format='png')
amp_graph.seek(0)
plt.close()
amp_graph_reader = ImageReader(amp_graph)

#create symmetry graph
plt.figure(figsize=(6,2))
plt.plot(Dashboard['UDK #'], Dashboard['Symmetry'], marker='o', linestyle='-')
plt.xlabel('UDK #')
plt.ylabel('% Symmetry')
plt.title('Symmetry | <100 = bigger downkick | >100 = bigger upkick')
plt.ylim(0,150)
plt.axhline(y=100, color='red', linestyle='--', linewidth=1)

sym_graph = BytesIO()
plt.savefig(sym_graph, format='png')
sym_graph.seek(0)
plt.close()
sym_graph_reader = ImageReader(sym_graph)

#generate report
destination_folder = r'D:\yolov8-gpu\UWDK_Pose'
pdf_filename = os.path.join(destination_folder, 'Grieshop_BK_T1.pdf')
pdf = canvas.Canvas(pdf_filename, pagesize=letter)
pdf.drawImage(ImageReader(vel_graph), 0, 250)
pdf.showPage()
pdf.drawImage(ImageReader(tempo_graph), 100, 450)
pdf.drawImage(ImageReader(amp_graph), 100, 225)
pdf.drawImage(ImageReader(sym_graph), 0, 10)

pdf.save()