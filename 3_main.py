# Python software driver for the Raspberry Pi Action Camera
# Current revision: 03 - Image capture and setting only / 13 October 2014
# All rights reserved
# Revision history:
# 00 - 	Project started 02 August 2014 - Capture images and video with default settings
# 01 - 	Added phisical buttons and maped to GPIO pins, Control of device through these buttons
#	Created preliminary skeleton of device main menu plus image capture, video record and image settings submenus
#	Implemented video record with circular IO (stop recording at buttom press)
# 02 -  Added LCD 16x2 display
# 03 - Solved navigation in menu, making image settings, capture image
#####################################################################################################
# module imports
import io 
import time 
import picamera 
import lcd
import RPi.GPIO as GPIO
from select import select
from fractions import Fraction

global starting_point
global ending_point
global temporary_sel

###################################################################################################
# auxiliar functions
def GPIO_pin_assignment(): #function to assign pins
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(11, GPIO.IN, GPIO.PUD_UP) #selection button 1
	GPIO.setup(15, GPIO.IN, GPIO.PUD_UP) #selection button 2
	GPIO.setup(13, GPIO.IN, GPIO.PUD_UP) #enter button

def GPIO_pin_init(): #funtion to initialize GPIO pins
	GPIO_pin_assignment()
	global select_button_1
	global select_button_2
	global enter_button
	select_button_1 = GPIO.input(11)
	select_button_2 = GPIO.input(15)
	enter_button = GPIO.input(13)

def filenamegen(file_type): #function to generate image or video filename
	path='/home/alexandru_gaal/camera_test/'
	name_index=time.strftime("%Y%m%d_%H%M%S")
	return path+file_type+name_index

def image_capture(res,iso,awb,spe,sat,sha,sce): #function to take a snapshot
        '''spe = 1000000
        res = (1280,720)
        sce = 'off'
        iso = 0'''
        print 'iso =', iso
        print 'resolution =', res
        print 'awb =', awb
        print 'speed =', spe
        print 'saturation =', sat
        print 'sharpness =', sha
        print 'scean =', sce
	file=filenamegen('IMG_')+'.jpg'
	with picamera.PiCamera() as camera:
                camera.start_preview()
                camera.resolution = res
                if (spe > 1000000) or (spe == 1000000):
                        camera.framerate = Fraction(1,spe/1000000) #needed to set minimum shutter speed
                        print 'slow exposure',camera.framerate
                elif (spe > 0) and (spe < 1000000):
                        camera.framerate = Fraction(spe,1000000)
                        print 'fast exposure',camera.framerate
                elif spe == 0:
                        camera.framerate = Fraction(1,100) #needed in case the shutter speed is set to 0 (auto)
                        print 'auto fps', camera.framerate
                else:
                        print 'Serious framerate error'
                camera.shutter_speed = spe
                camera.exposure_mode = sce
                camera.ISO = iso
                camera.awb_mode = awb
                camera.saturation = sat
                camera.sharpness = sha
                time.sleep(2)
        	camera.capture(file)
                time.sleep(0.1)
      		camera.stop_preview()
	return None

def display(text1,text2,text3): # WIP, function will contain commands for displaying information on the LCD
        lcd.pin_setup()
	lcd.init()
	text1 = str(text1)
	text2 = str(text2)
	text3 = str(text3)
	if len(text1) > 7:
		text1 = text1[0:7]
	if len(text2) > 7:
		text2 = text2[0:7]
	if len(text3) > 13:
		text3 = text3[0:13]
	lcd.display(text1+(8-len(text1)-1)*' '+'::'+(8-len(text2)-1)*' '+text2,1,'left')
	lcd.display('=> '+text3,2,'center')

def go_back():
        global starting_point #needed to define menu left limit
        global ending_point #needed to define menu right limit
        global temporary_sel #needed to define current position in the menu
        starting_point=0
        ending_point=5
        temporary_sel=starting_point+1

def image_settings(): # Function containing the branches of image setting
        global starting_point
        global ending_point
        global temporary_sel
        starting_point = 30
        ending_point = 37
	temporary_sel = starting_point+1
	
def video_settings(): # Function containing the brenches for video setting
	print 'Video settings'
def device_settings(): # Function containing the brenches for device settings
	print 'Device settings'
def power_off(): # Function containing the commands to safely power off the device
	print 'Power off'

def adjustment(available_options,default_option,nr_of_parameters):
        # available_options is a dictionary with the possible options for a setting, e. resolution
        # every dictionery item is a list with the [0] position being the value name / description
        # [1] and/or [2] is the value for the option
        # ex: image_resolutions={1:['1 Mp 4:3',1160,870],...,11:['5 Mp 4:3',2592,1944]}
	global menu_delay
	GPIO_pin_assignment() #assigning GPIO pins
	lcd.pin_setup()
	lcd.init()
        display('(-) <-','-> (+)',available_options[default_option][0])
        current_option = default_option
	button_press = True
        while True:
                GPIO_pin_init()
                lcd.pin_setup()
                if button_press:
                        display('(-) <-','-> (+)',available_options[current_option][0])
                        button_press = False
                time.sleep(menu_delay)
                if select_button_1 == False: # selection to RIGHT
                        button_press = True
                        if current_option < len(available_options):
                                current_option += 1
		if select_button_2 == False: # selection to LEFT 
                        button_press = True
                        if current_option > 1:
                                current_option -= 1
                if enter_button == False:
                        if nr_of_parameters == 2:
                                return  available_options[current_option][1],available_options[current_option][2]
                        else:
				return  available_options[current_option][1]

			
###############################################################
#Here starts the main program
			
#dictionary with possible image settings
image_resolutions={1:['1 Mp 4:3',1160,870],2:['2 Mp 4:3',1635,1226],3:['2.3 Mp 16:9 UW',2000,1125],4:['2.7 Mp 3:2 W',2000,1333],5:['3 Mp 4:3',2000,1500],6:['3 Mp 16:9 UW',2320,1305],7:['3.6 Mp 3:2 W',2320,1547],8:['4 Mp 4:3',2320,1740],9:['4 Mp 16:9 UW',2592,1458],10:['4.5 Mp 3:2 W',2592,1728],11:['5 Mp 4:3',2592,1944]}
scene_modes={1:['AUTO','auto'],2:['Manual','off'],3:['ANTI SHAKE','antishake'],4:['FIXED FPS','fixedfps'],5:['VERY LONG','verylong'],6:['BEACH','beach'],7:['SNOW','snow'],8:['SPORTS','sports'],9:['SPOTLIGHT','spotlight'],10:['BACKLIGHT','backlight'],11:['NIGHT','night'],12:['FIREWORKS','fireworks']}
shutter_speeds={1:['AUTO',0],2:['1/4000 s',250],3:['1/2000 s',500],4:['1/1000 s',1000],5:['1/500 s',2000],6:['1/250 s',4000],7:['1/100 s',10000],8:['1/50 s',20000],9:['1/20 s',50000],10:['1/10 s',100000],11:['1/5 s',200000],12:['1/2 s',500000],13:['1 s',1000000],14:['2 s',2000000],15:['5 s',5000000],16:['10 s',10000000],17:['30 s',30000000],18:['60 s',60000000]}
ISO_speeds={1:['AUTO',0],2:['100',100],3:['200',200],4:['400',400],5:['500',500],6:['640',640],7:['800',800]}
WB_modes={1:['AUTO','auto'],2:['SUNLIGHT','sunlight'],3:['CLOUDY','cloudy'],4:['SHADE','shade'],5:['TUNGSTEN','tungsten'],6:['FLUORESCENT','fluorescent'],7:['INCANDESCENT','incandescent'],8:['FLASH','flash'],0:['HORIZON','horizon']}
image_sharpness={1:['-100',-100],2:['-75',-75],3:['-50',-50],4:['-25',-25],5:['00',0],6:['25',25],7:['50',50],8:['75',75],9:['100',100]}
image_saturation={1:['-100',-100],2:['-75',-75],3:['-50',-50],4:['-25',-25],5:['00',0],6:['25',25],7:['50',50],8:['75',75],9:['100',100]}

#dictionary with menu text content
left_option={0:'OFF',1:'CAPTURE',2:'RECORD',3:'IMG SET',4:'VID SET',5:'DEV SET',
             30:'BACK',31:'SCENE',32:'RESOL',33:'SPEED',34:'ISO',35:'WB',36:'SHARP',37:'SATUR'}
right_option={0:'OFF',1:'CAPTURE',2:'RECORD',3:'IMG SET',4:'VID SET',5:'DEV SET',
              30:'BACK',31:'SCENE',32:'RESOL',33:'SPEED',34:'ISO',35:'WB',36:'SHARP',37:'SATUR'}
middle_option={0:'POWER OFF',1:'IMG CAPTURE',2:'VID RECORD',3:'IMG SETTINGS',4:'VID SETTINGS',5:'DEV SETTINGS',
               30:'GO BACK',31:'AUTO SCENE',32:'RESOLUTION',33:'SHUTTER SPEED',34:'ISO SPEED',35:'WHITE BALANCE',36:'SHARPNESS',37:'SATURATION'}

#defaul image setting values
img_res = (image_resolutions[11][1],image_resolutions[11][2])
img_ISO = ISO_speeds[1][1]
img_awb = WB_modes[1][1]
img_speed  = shutter_speeds[1][1]
img_satur = image_saturation[5][1]
img_sharp = image_sharpness[5][1]
img_scene = scene_modes[1][1]

GPIO_pin_assignment() #assigning GPIO pins
lcd.pin_setup()
lcd.init()
go_back() # need to run this function to set initial menu limits
left_sel = starting_point + 1
right_sel = starting_point + 3

#Legend: 0-Power off, 1-Image, 2-Video, 3-Image settings, 4-Video settings, 5-Device_settings
button_press = False
menu_delay = 0.2

display(left_option[left_sel],right_option[right_sel],middle_option[temporary_sel])

while True:
	GPIO_pin_init()
	lcd.pin_setup()
	if button_press:
		display(left_option[left_sel],right_option[right_sel],middle_option[temporary_sel])
		button_press = False
	time.sleep(menu_delay)
	if select_button_1 == False: # selection to RIGHT
		button_press = True
		if temporary_sel == ending_point:
			temporary_sel = starting_point
			left_sel = ending_point
			right_sel = temporary_sel + 1
		else:
			left_sel = temporary_sel
			temporary_sel = temporary_sel + 1
			if temporary_sel == ending_point:
				right_sel = starting_point
			else:
				right_sel = temporary_sel + 1

	if select_button_2 == False: # selection to LEFT
		button_press = True
		if temporary_sel == starting_point:
			right_sel = temporary_sel
			temporary_sel = ending_point
			left_sel = temporary_sel - 1
		else:
			right_sel = temporary_sel
			temporary_sel = temporary_sel - 1
			if temporary_sel == starting_point:
				left_sel = ending_point
			else:
				left_sel = temporary_sel - 1
	if enter_button == False:
		button_press = True
                f=function_list[temporary_sel]
	        if 'var' in f:
                        for key,variable in f.iteritems():
                                if variable == 'var':
                                        globals()[key]=f['func'](*f['args'])
                                        print 'variable is',key
	        elif 'args' in f:
                        f['func'](*f['args'])
                else:
                        f['func']()
                left_sel = temporary_sel - 1
                right_sel = temporary_sel + 1

        function_list={0:{'func':power_off},
               1:{'func':image_capture,'args':(img_res,img_ISO,img_awb,img_speed,img_satur,img_sharp,img_scene)}, #(res,iso,awb,spe,sat,sha,sce)
               2:{'func':display,'args':('WIP!!!','WIP!!!','VIDEO')}, #WIP
               3:{'func':image_settings},
               4:{'func':video_settings}, #WIP
               5:{'func':device_settings}, #WIP
               30:{'func':go_back},
               31:{'func':adjustment,'args':(scene_modes,1,1),'var':'','img_scene':'var'},
               32:{'func':adjustment,'args':(image_resolutions,11,2),'var':'','img_res':'var'},
               33:{'func':adjustment,'args':(shutter_speeds,1,1),'var':'','img_speed':'var'},
               34:{'func':adjustment,'args':(ISO_speeds,1,1),'var':'','img_ISO':'var'},
               35:{'func':adjustment,'args':(WB_modes,1,1),'var':'','img_awb':'var'},
               36:{'func':adjustment,'args':(image_sharpness,5,1),'var':'','img_sharp':'var'},
               37:{'func':adjustment,'args':(image_saturation,5,1),'var':'','img_satur':'var'}}
