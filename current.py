import argparse
from contextlib import nullcontext
from glob import glob
from io import TextIOWrapper, BufferedRWPair
from serial import Serial
from serial.tools.list_ports import comports
from ursina import *
from ursina import curve, shaders
import matplotlib.pyplot as plt
import csv
from datetime import datetime
# Download the helper library from https://www.twilio.com/docs/python/install
import os
import twilio
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = "ACcf29a9e7cbbe84e458313189eef744ca"
auth_token = "04eff2d3d480ffdcfc5b3d1605a489e6"
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="We have detected that you are not moving your head. Please check your head position and try again.",
                     from_='+19853045931',
                     to='+15713830830'
                 )

f = open('Data.csv', 'w')
writer = csv.writer(f)
ψ_prev=-999999
θ_prev=-999999
φ_prev=-999999
accb=-999999 
time = 0



threshold = 10;
count=0;
def get_arduino_port():
    return next(port.device for port in comports() if "Arduino" in port.description)

parser = argparse.ArgumentParser()

parser.add_argument("--port", "-p",
    help = "the id of the port the device is on (default: guess)",
)

parser.add_argument("--baud", "-b",
    help    = "the device's serial baudrate (default: 9600)",
    default = 9600
)

parser.add_argument("--delimiter","-d",
    help    = 'the csv-style delimiter (you may need to enter this in quotes; default: ",")',
    default = ","
)

parser.add_argument("--sample-rate", "-s",
    help    = "the rate in Hz at which the device sends output (default: 8000)",
    default = 8000
)

parser.add_argument("--ready-flag", "-f",
    help    = "any unique part of the serial output string that signals the that the device is done calibrating (default: pitch)",
    default = "pitch"
)
def is_spike(ψ, θ, φ, ψb, θb, φb,acc,accb,list):
    


    global count
    thresholdSpeed=10000
    global threshold
    threshold=2
    if(ψb==-999999 or acc==-999999):
        return False
    elif(abs(ψb-ψ)>threshold or abs(θb-θ)>threshold or abs(φb-φ)>threshold or abs(acc-accb)>thresholdSpeed):
        count+=1
        if(count>20):
            print(message.sid)
            list.append("SPIKE")
            writer.writerow(list)
            return True
            

            

        writer.writerow(list)   
        return False
    else:
        count=0;
        writer.writerow(list)
        return False



    return abs(ψ) > 10 or abs(θ) > 10 or abs(φ) > 10
args = parser.parse_args()

port        = get_arduino_port() if not args.port or args.port == "guess" else args.port
baud        = args.baud
delimiter   = args.delimiter
sample_rate = args.sample_rate
ready_flag  = args.ready_flag

sample_time = 1 / sample_rate

def serial_buffer(serial):
    return TextIOWrapper(BufferedRWPair(serial, serial))

def fallback_row(buffer, minimum_columns, last_row):
    if last_row is None:
        row = read_row(buffer, minimum_columns)
    else:
        row = last_row
    return row

def read_row(buffer, minimum_columns=0, last_row=None):
    try:
        values = buffer.readline().strip().split(delimiter)
        
        if len(values) < minimum_columns:
            row = fallback_row(buffer, minimum_columns, last_row)
        else:
            row = [float(value) for value in values]
            
        last_row = row
    except:
        row = fallback_row(buffer, minimum_columns, last_row)
    return row

serial = Serial(port, baud, timeout=sample_time)

buffer = serial_buffer(serial)
buffer.readline() # sync

class Spinner(Entity):
    ψ_prev=-999999
    θ_prev=-999999
    φ_prev=-999999

    def __init__(self, inactive_message, active_model, active_scale, active_color, alternate_shader, *args, **kwargs):
        global ψ_prev, θ_prev, φ_prev
        θ_prev=-999999
        φ_prev=-999999
        ψ_prev=-999999
        self.update = self.wait
        
        self.inactive_message = Text(
            text     = inactive_message,
            origin   = (0, 0),
            position = window.center - (0, 1/5)
        )
        
        self.data_display = Text(
            text     = "ψ =    0.00°    θ =    0.00°    φ =    0.00°",
            origin   = (0, -1),
            position = window.bottom,
            font     = "FiraMono.ttf"
        )
        
        self.active_model = active_model
        self.active_scale = active_scale
        self.active_color = active_color
        
        self.alternate_shader = alternate_shader
        
        super(Spinner, self).__init__(*args, **kwargs)
        
        self.animate_rotation(self.rotation + (0, 0, 90), 1, loop=True, curve=curve.in_out_quint)
        
    def spin(self):
        global ψ_prev, θ_prev, φ_prev , accb
        ψ_raw, θ_raw, φ_raw, temp, acc= read_row(buffer, 5)[0:5]
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        """save temp in a csv file with the time"""
        writeList=[ψ_raw, θ_raw, φ_raw, temp, acc,current_time]


        

        
        
        #use mathplotlib to get live temp data and graph with the line being red live
        # plt.plot(temp, 'r')
        
        # plt.ylabel('Temperature')
        # plt.xlabel('Time')
        # plt.show()

        
        ψ = -ψ_raw
        
        θ =  θ_raw
        φ =  φ_raw
        
        
       
        if(is_spike(ψ, θ, φ, ψ_prev, θ_prev, φ_prev,acc,accb,writeList)):
            print("QUIT")
            sys.exit()

       
        if(ψ!=None):
            ψ_prev, θ_prev, φ_prev = ψ, θ, φ
            accb=acc

        
        
        
        self.data_display.text = (
            "ψ = {:>7.2f}°    θ = {:>7.2f}°    φ = {:>7.2f}°  Temp= {:>7.2f}°C  Acc= {:>7.2f}g".format(ψ, θ, φ,temp,acc)
        )
        
        self.animate_rotation((ψ, θ, φ), sample_time, curve=curve.in_out_sine)

    def wait(self):
        line = buffer.readline()
        if line.count(ready_flag):
            destroy(self.inactive_message)
            
            self.color = self.active_color
            self.rotation = (0, 0, 0)
            self.animate_scale(self.active_scale, 0.2, curve=curve.out_cubic)
            self.model = self.active_model
            
            self.update = self.spin
            
    def input(self, key):
        if key == 'space':
            self.shader, self.alternate_shader = self.alternate_shader, self.shader

"""
takes in three floats, ψ, θ, φ, and if there is a big spike in any of the three it will return True
"""

app = Ursina()
window.color = color.black
window.fullscreen = False
window.fps_counter.enabled = False
window.borderless = False

Spinner(
    inactive_message = "calibrating—sensor must be still!",
    model            = "cube",
    active_model     = "icosphere",
    scale            = 1.5,
    active_scale     = 3,
    color            = color.red,
    active_color     = color.azure,
    shader           = shaders.lit_with_shadows_shader,
    alternate_shader = shaders.normals_shader
)

def close():
    serial.close()
    exit()

app.exitFunc = close

app.run()
