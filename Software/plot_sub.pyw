#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Damiano Lollini
# @Date:   25-01-2015 00:10:29
# @Last Modified by:   Damiano Lollini
# @Last Modified time: 25-01-2015 00:10:29



__author__ = 'Damiano Lollini'
__copyright__ = 'Copyright (c) 2015 Damiano Lollini'
__rev = "x"

import re
import time
import serial
from threading import Thread
import threading
import numpy as np

# tkinter gui
import tkinter as Tk
from tkinter import ttk, StringVar, BooleanVar
from tkinter.filedialog import askopenfilename, asksaveasfilename

# Load MatplotLib
import matplotlib

# matplotlib tkinter
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import sys, os, re
# chose an implementation, depending on os
if os.name == 'nt': #sys.platform == 'win32':
	from serial.tools.list_ports_windows import *
elif os.name == 'posix':
	from serial.tools.list_ports_posix import *
else:
	raise ImportError("Sorry: no implementation for your platform ('%s') available" % (os.name,))



class SerialData(object):
	def __init__(self, port='None', baudrate = 115200, timeout=None,
				bytesize = 8, parity = 'N', stopbits = 1,
				xonxoff=0, rtscts = 0):
		self.name     = port
		self.port     = port
		self.timeout  = timeout
		self.parity   = parity
		self.baudrate = baudrate
		self.bytesize = bytesize
		self.stopbits = stopbits
		self.xonxoff  = xonxoff
		self.rtscts   = rtscts



	def open(self):
		try:
			self.ser = ser = serial.Serial(
				self.port, self.baudrate, self.bytesize, self.parity, self.stopbits,
				self.timeout, self.xonxoff,self.rtscts)
			#print ("Connesso su porta: " + self.port)
		except serial.serialutil.SerialException:
			#no serial connection
			#print ("Eccezione serial open")
			self.ser = None


	def isOpen( self ):
		try:
			self._isOpen = self.ser.isOpen()
		except:
			self._isOpen = False
		#print(self._isOpen)
		return self._isOpen

	def close(self):
		#print("Serial close")
		try:
			if self.ser:
				self.ser.close()
		except:
			pass

	def write(self,string):
		self.ser.write(string.encode())

	def __del__(self):
		#print("Serial _del_")
		if self.ser:
			self.ser.close()


class App:
	def __init__(self,add_subplot=True, root=None, **kwargs):
		args = kwargs

		# variabili
		self.gyro_buff = ""
		self.acc_buff = ""
		self.mag_buff = ""
		self.ultra_buff =""

		# variabile per i dati dalla seriale
		self.LINE = ""
		self.N_BYTE_RX = 38

		# SENSITIVITY per un dato fondoscala
		#self.sens_acc = 1				# per ±2 g              -> [mg/LSB]
		self.sens_acc = 16				# per la formula
		self.sens_mag = 205				# per ±8.1 gauss        -> [LSB/gauss]
		self.sens_gyro = 17.5			# per ±500 dps          -> [mdps/LSB]

		# FORMULE:
		# ACC = ( (1/SENSITIVITY) * (REG) ) / 16 -> (12 bit rappresentation)  [mg]
		# MAG = ( (REG) * 1000) / SENSITIVITY                                 [mgauss]
		# GYRO = ( (REG) * SENSITIVITY ) / 1000                               [dps]




		# numero di campioni da visualizzare
		self.maxLen = 100
		self.dataplot = np.zeros(shape=(6,self.maxLen))

		# limite assi 
		self.x_point = self.maxLen
		self.y_acc_min = -2000			# [mg]
		self.y_acc_max = 2000			# [mg]
		self.y_gyro_min = -500			# [dps]
		self.y_gyro_max = 500			# [dps]

		# matrice da 4 righe per self.maxlen colonne
		# 1° riga : accx 
		# 2° riga : accy 
		# 3° riga : accz 
		# 4° riga : gyrox
		# 5° riga : gyroy
		# 6° riga : gyroz
		# es: 
		# self.maxLen = 3, this is dataplot:
		# 	[[ 0.  0.  0. ]		--> accx
 		#	 [ 0.  0.  0. ]		--> accy
 		#	 [ 0.  0.  0. ]		--> accz
		# 	 [ 0.  0.  0. ]		--> gyrox
 		#	 [ 0.  0.  0. ]		--> gyroy
 		#	 [ 0.  0.  0. ]]	--> gyroz

		# personalizzaione plot
		self.font_title = {
		'family' : 'serif',
		'color'  : 'white',
		'weight' : 'normal',
		'size'   : 20,
		}


		self.font_assi = {
		'family' : 'serif',
		'color'  : 'white',
		'weight' : 'normal',
		'size'   : 12,
		}

		legend_color = 'grey'
		legend_pos = "upper left"
		legend_font_size = 12
		legend_text_color = "white"
		fig_color = '#07000d'
		line_width = 1
		spine_color = "#5998ff"
		grid_color = 'w'


		# array per legenda
		self.list_acc = ["Acc_x [mg]","Acc_y [mg]","Acc_z [mg]"]
		self.list_gyro = ["Gyro_x [dps]","Gyro_y [dps]","Gyro_z [dps]"]
		self.list_line_color = ['y','r','g']

		# Label
		self.lbl_stato_conn_on = "Stato connessione: CONNESSO alla porta "
		self.lbl_stato_conn_off = "Stato connessione: DISCONNESSO"
		self.lbl_serial_setting = "Default COM 115200/8-N-1"

		# grafico
		self.fig = matplotlib.figure.Figure(figsize=(4,5),dpi=80)
		self.fig.set_facecolor(fig_color)
		self.fig.subplots_adjust(bottom=0.08, left=0.08,right=0.96,top=0.91,hspace=0.35)

		# due grafici uno per l'accelerazione e uno per il gyroscopio
		self.ax0 = self.fig.add_subplot(211,axisbg=fig_color)
		self.ax1 = self.fig.add_subplot(212,axisbg=fig_color, sharex = self.ax0)

		# titolo
		self.ax0.set_title('Grafico Accelerometro', fontdict=self.font_title)
		self.ax1.set_title('Grafico Gyroscopio', fontdict=self.font_title)



		for ax in self.ax0, self.ax1:
			ax.tick_params(axis='y', colors='w')
			ax.tick_params(axis='x', colors='w')
			ax.spines['bottom'].set_color(spine_color)
			ax.spines['left'].set_color(spine_color)
			ax.spines['top'].set_color(spine_color)
			ax.spines['right'].set_color(spine_color)

			if ax == self.ax0:
				for text, color in zip(self.list_acc,self.list_line_color):
					ax.plot([], [],color,label=text,linewidth=line_width)
			else:
				for text, color in zip(self.list_gyro,self.list_line_color):
					ax.plot([], [],color,label=text,linewidth=line_width)

			# disegna una griglia
			ax.grid(True, color=grid_color)

			ax.leg = ax.legend(loc=legend_pos,shadow=True,fontsize=legend_font_size,labelspacing=0.2)
			ax.leg.get_frame().set_facecolor(legend_color)
			ax.leg.get_frame().set_alpha(0.4)
			ax.leg.get_frame().set_edgecolor('w')
			for text in ax.leg.get_texts():
				text.set_color(legend_text_color)



		# TK gui
		######################################################
		self.window = Tk.Tk()
		self.window.wm_title("PLOT gui")
		self.window.resizable(width='false', height='false')
		self.window.iconbitmap("img\plot.ico")

		# il grafico è in ROW=0 con un frame tk
		#########################################
		self.figure_frame = ttk.Frame(self.window)

		self.canvas = FigureCanvasTkAgg(self.fig, master=self.figure_frame)
		self.canvas._tkcanvas.pack(side=Tk.TOP,  fill=Tk.BOTH, expand=0)

		self.figure_frame.columnconfigure(0, weight=0) # colonna 0 non si espande
		self.figure_frame.rowconfigure(0, weight=0) # riga 0 non si espande

		self.Frame_cmd = ttk.Frame(master=self.window, relief='groove', borderwidth=2)
		#ttk.Label(self.Frame_cmd, text = 'Invio cmd').grid(pady=0)
		self.Button_START = ttk.Button(master=self.Frame_cmd,text='START',command=self.e_start_send)
		self.Button_STOP = ttk.Button(master=self.Frame_cmd,text='STOP',command=self.e_stop_send)

		self.Frame_port = ttk.Frame(master=self.window, relief='groove', borderwidth=2)
		self.label_connessione = ttk.Label(master=self.Frame_port,text=self.lbl_stato_conn_off)
		self.label_ser_setting = ttk.Label(master=self.Frame_port,text=self.lbl_serial_setting)
		self.Button_connetti = ttk.Button(master=self.Frame_port,text='Connetti',command=self.e_connetti)
		self.Button_disconnetti = ttk.Button(master=self.Frame_port,text='Disconnetti',command=self.e_disconnetti)
		self.Button_aggiornaporte = ttk.Button(master=self.Frame_port,text='Aggiorna Porte',command=self.e_elenco_porte)

		self.Frame_List_port = ttk.Frame(master=self.Frame_port)
		dataCols = ("PORTA","DESCRIZIONE")
		col_dist = (60,320)
		self.tree = ttk.Treeview(master=self.Frame_List_port, height="3", columns=dataCols, show='headings')
		for (c,k) in zip(dataCols,col_dist):
			self.tree.heading(c,text=c,anchor='w')
			self.tree.column(c,width=k)
		ysb = ttk.Scrollbar(master=self.Frame_List_port, orient='vertical', command= self.tree.yview)
		xsb = ttk.Scrollbar(master=self.Frame_List_port, orient='horizontal', command= self.tree.xview)
		self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
		self.tree.bind('<<TreeviewSelect>>', self.e_select_port)

		self.Frame_type_graph = ttk.Frame(master=self.window, relief='groove', borderwidth=2)

		self.check_accx = BooleanVar()
		self.check_accy = BooleanVar()
		self.check_accz = BooleanVar()
		self.Checkb_accx = ttk.Checkbutton(master=self.Frame_type_graph,text=self.list_acc[0], variable=self.check_accx, command= lambda: self.e_add_acc(self.check_accx,1))
		self.Checkb_accy = ttk.Checkbutton(master=self.Frame_type_graph,text=self.list_acc[1], variable=self.check_accy, command= lambda: self.e_add_acc(self.check_accy,2))
		self.Checkb_accz = ttk.Checkbutton(master=self.Frame_type_graph,text=self.list_acc[2], variable=self.check_accz, command= lambda: self.e_add_acc(self.check_accz,3))


		self.check_gyrox = BooleanVar()
		self.check_gyroy = BooleanVar()
		self.check_gyroz = BooleanVar()
		self.checkb_gyrox = ttk.Checkbutton(master=self.Frame_type_graph,text=self.list_gyro[0], variable=self.check_gyrox, command= lambda: self.e_add_gyro(self.check_gyrox,1))
		self.checkb_gyroy = ttk.Checkbutton(master=self.Frame_type_graph,text=self.list_gyro[1], variable=self.check_gyroy, command= lambda: self.e_add_gyro(self.check_gyroy,2))
		self.checkb_gyroz = ttk.Checkbutton(master=self.Frame_type_graph,text=self.list_gyro[2], variable=self.check_gyroz, command= lambda: self.e_add_gyro(self.check_gyroz,3))

		self.lbl_val_accx = StringVar()
		self.lbl_val_accy = StringVar()
		self.lbl_val_accz = StringVar()
		self.label_accx = ttk.Label(master=self.Frame_type_graph,textvariable=self.lbl_val_accx, width=8)
		self.label_accy = ttk.Label(master=self.Frame_type_graph,textvariable=self.lbl_val_accy, width=8)
		self.label_accz = ttk.Label(master=self.Frame_type_graph,textvariable=self.lbl_val_accz, width=8)

		self.lbl_val_gyrox = StringVar()
		self.lbl_val_gyroy = StringVar()
		self.lbl_val_gyroz = StringVar()
		self.label_gyrox = ttk.Label(master=self.Frame_type_graph,textvariable=self.lbl_val_gyrox, width=8)
		self.label_gyroy = ttk.Label(master=self.Frame_type_graph,textvariable=self.lbl_val_gyroy, width=8)
		self.label_gyroz = ttk.Label(master=self.Frame_type_graph,textvariable=self.lbl_val_gyroz, width=8)

		self.label_text_val = [self.lbl_val_accx, self.lbl_val_accy, self.lbl_val_accz,
								self.lbl_val_gyrox, self.lbl_val_gyroy, self.lbl_val_gyroz]
		for x in self.label_text_val:
			x.set("0000")


		self.Frame_xy = ttk.Frame(master=self.window, relief='groove', borderwidth=2)
		self.Entry_xpoint = ttk.Entry(self.Frame_xy,textvariable=self.x_point,width=5)
		self.Entry_acc_ymin = ttk.Entry(self.Frame_xy,textvariable=self.y_acc_min,width=5)
		self.Entry_acc_ymax = ttk.Entry(self.Frame_xy,textvariable=self.y_acc_max,width=5)
		self.Entry_gyro_ymin = ttk.Entry(self.Frame_xy,textvariable=self.y_gyro_min,width=5)
		self.Entry_gyro_ymax = ttk.Entry(self.Frame_xy,textvariable=self.y_gyro_max,width=5)
		self.Button_updatesoglia = ttk.Button(master=self.Frame_xy,text='Aggiorna limite assi',command=self.e_get_xy)

		########## logo e label
		self.about_lbl = ttk.Label(master=self.window,text="Copyright Damiano Lollini",foreground="red",font=('Helvetica',8))
		self.about_lbl.grid(row=8,column=3,columnspan=2, padx=10, sticky=("E"))

		########## array
		self.array_check_acc = [self.check_accx,self.check_accy,self.check_accz]
		self.array_check_gyro = [self.check_gyrox,self.check_gyroy,self.check_gyroz]





		##############################  griglia  ##############################
		self.figure_frame.grid(row=0, column=0, columnspan=4 ,sticky=(Tk.N, Tk.S, Tk.E, Tk.W))


				##### Frame_cmd
		self.Frame_cmd.grid(row=1, column=0, padx = 5, pady = 5, rowspan=4, sticky=("E","W","S","N"))
		self.Button_START.grid(row=0, column=0, padx = 5,pady = 10, sticky=("EW"))
		self.Button_STOP.grid(row=1, column=0, padx = 5,pady = 10, sticky=("EW"))


				##### Frame_type_graph
		self.Frame_type_graph.grid(row=1, column=1, padx = 5, pady = 5, sticky=(Tk.N, Tk.S, Tk.E, Tk.W))

		self.Checkb_accx.grid(row=3,column=0, padx=5, sticky=("W"))
		self.Checkb_accy.grid(row=4,column=0, padx=5, sticky=("W"))
		self.Checkb_accz.grid(row=5,column=0, padx=5, sticky=("W"))

		self.label_accx.grid(row=3,column=1, padx=5, sticky=("W"))
		self.label_accy.grid(row=4,column=1, padx=5, sticky=("W"))
		self.label_accz.grid(row=5,column=1, padx=5, sticky=("W"))

		self.checkb_gyrox.grid(row=3,column=2, padx=5, sticky=("W"))
		self.checkb_gyroy.grid(row=4,column=2, padx=5, sticky=("W"))
		self.checkb_gyroz.grid(row=5,column=2, padx=5, sticky=("W"))

		self.label_gyrox.grid(row=3,column=3, padx=5, sticky=("W"))
		self.label_gyroy.grid(row=4,column=3, padx=5, sticky=("W"))
		self.label_gyroz.grid(row=5,column=3, padx=5, sticky=("W"))


				##### Frame_xy
		self.Frame_xy.grid(row=1, column=2,pady = 5, sticky=("E","S","N"))
		self.Button_updatesoglia.grid(row=0,column=0, padx=5, pady=5, sticky=("WE"))
		ttk.Label(master=self.Frame_xy,text="Punti asse x").grid(row=2,column=0, padx=5, sticky=("W"))
		self.Entry_xpoint.grid(row=2,column=0, padx=5, sticky=("E"))
		# acc
		ttk.Label(master=self.Frame_xy,text="ymin_acc").grid(row=3,column=0, padx=5, sticky=("W"))
		self.Entry_acc_ymin.grid(row=3,column=0, padx=5, sticky=("E"))
		ttk.Label(master=self.Frame_xy,text="ymax_acc").grid(row=4,column=0, padx=5, sticky=("W"))
		self.Entry_acc_ymax.grid(row=4,column=0, padx=5, sticky=("E"))
		# gyro
		ttk.Label(master=self.Frame_xy,text="ymin_gyro").grid(row=5,column=0, padx=5, sticky=("W"))
		self.Entry_gyro_ymin.grid(row=5,column=0, padx=5, sticky=("E"))
		ttk.Label(master=self.Frame_xy,text="ymax_gyro").grid(row=6,column=0, padx=5, sticky=("W"))
		self.Entry_gyro_ymax.grid(row=6,column=0, padx=5, sticky=("E"))


				##### Frame_port -> Frame_List_port
		self.Frame_port.grid(row=1, column=3, pady = 5, padx = 5, rowspan=4, sticky=("E","S","N"))
		self.label_connessione.grid(row=0, column=0,columnspan=2,sticky=("W"))
		self.label_ser_setting.grid(row=0, column=1, columnspan=2, sticky=("E"))
		self.Button_connetti.grid(row=1, column=0, padx=5, pady = 0, sticky=("E","W"))
		self.Button_disconnetti.grid(row=2, column=0, padx=5, pady = 0, sticky=("E","W"))
		self.Button_aggiornaporte.grid(row=3, column=0,  padx=5, pady = 0, sticky=("E","W"))
		self.Frame_List_port.grid(row=1, column=1, padx=5, rowspan=4, sticky=("E","W","S","N"))
		self.tree.grid(row=0, column=0, rowspan=4, sticky=("E","W","S","N"))
		ysb.grid(row=0, column=1, rowspan=4, sticky='NS')




		self.e_elenco_porte()
		self.non_connesso()
		self.update_xy()
		self.reset_graph()



	######## funzioni eventi oggetti

	def e_start_send(self):
		#print("button Start")
		try:
			if (self.SERIAL_SER.isOpen()):
				self.SERIAL_SER.ser.flushInput()
				THREAD_event_serial.set()
				#self.SERIAL_SER.write("START")
				self.Button_START.config(state = "disabled")
				self.Button_STOP.config(state = "enabled")
			else:
				self.non_connesso()
		except:
			self.non_connesso()



	def e_stop_send(self):
		#print ("button Stop")
		try:
			if (self.SERIAL_SER.isOpen()):
				THREAD_event_serial.clear()
				THREAD_event_graph.clear()
				#self.SERIAL_SER.write("STOP!")
				self.Button_START.config(state = "enabled")
				self.Button_STOP.config(state = "disabled")
			else:
				self.non_connesso()
		except:
			self.non_connesso()


	def e_get_xy(self):
		temp_x_point=int(self.Entry_xpoint.get())
		temp_y_acc_min=int(self.Entry_acc_ymin.get())
		temp_y_acc_max=int(self.Entry_acc_ymax.get())
		temp_y_gyro_min=int(self.Entry_gyro_ymin.get())
		temp_y_gyro_max=int(self.Entry_gyro_ymax.get())
		# numero di punti
		if (temp_x_point>self.maxLen):
			temp_x_point = self.maxLen
		# controllo y acc
		if (temp_y_acc_min < temp_y_acc_max) and ( 0 <= temp_x_point):
			self.x_point = temp_x_point
			self.y_acc_max = temp_y_acc_max
			self.y_acc_min = temp_y_acc_min
		# controllo y gyro
		if (temp_y_gyro_min < temp_y_gyro_max) and ( 0 <= temp_x_point):
			self.x_point = temp_x_point
			self.y_gyro_max = temp_y_gyro_max
			self.y_gyro_min = temp_y_gyro_min
		self.update_xy()


	def update_xy(self):
		self.Entry_xpoint.delete(0,5)
		self.Entry_acc_ymin.delete(0,5)
		self.Entry_acc_ymax.delete(0,5)
		self.Entry_gyro_ymin.delete(0,5)
		self.Entry_gyro_ymax.delete(0,5)
		self.Entry_xpoint.insert(0,self.x_point)
		self.Entry_acc_ymin.insert(0,self.y_acc_min)
		self.Entry_acc_ymax.insert(0,self.y_acc_max)
		self.Entry_gyro_ymin.insert(0,self.y_gyro_min)
		self.Entry_gyro_ymax.insert(0,self.y_gyro_max)
		self.ax0.set_xlim(0,self.x_point)
		self.ax0.set_ylim(self.y_acc_min,self.y_acc_max)
		self.ax1.set_xlim(0,self.x_point)
		self.ax1.set_ylim(self.y_gyro_min,self.y_gyro_max)
		# tick sulle coordinate
		grx = (self.x_point)/20
		gry = (self.y_acc_max-self.y_acc_min)/8
		self.ax0.set_xticks(np.arange(0,self.x_point,grx))
		self.ax0.set_yticks(np.arange(self.y_acc_min,self.y_acc_max,gry))
		gry = (self.y_gyro_max-self.y_gyro_min)/8
		self.ax1.set_xticks(np.arange(0,self.x_point,grx))
		self.ax1.set_yticks(np.arange(self.y_gyro_min,self.y_gyro_max,gry))
		# disegna
		self.fig.canvas.draw()


	def e_connetti(self):
		#print ("button Connetti")
		SERIAL_PORT = self.select_port()
		try:
			if not (SERIAL_PORT == "None"):
				self.SERIAL_SER = SerialData(SERIAL_PORT)
				self.SERIAL_SER.open()
				if (self.SERIAL_SER.isOpen()):
					self.label_connessione['text'] = self.lbl_stato_conn_on + SERIAL_PORT
					self.connesso()
					self.SERIAL_SER.ser.flush()
				else:
					self.non_connesso()
		except:
			self.non_connesso()


	def e_disconnetti(self):
		#print ("button Disconnetti")
		THREAD_event_serial.clear()
		THREAD_event_graph.clear()
		try:
			self.SERIAL_SER.close()
		except:
			pass
		self.non_connesso()


	def e_elenco_porte(self):
		self.tree.delete(*self.tree.get_children());
		lista_porte_seriali = sorted(comports())
		#print (lista_porte_seriali)
		for item in lista_porte_seriali:
			self.tree.insert('', 'end', values=item)


	def e_select_port(self,event):
		self.select_port()


	# del/add graph
	def e_add_acc(self,var,line):
		if var.get():
			self.ax0.lines[line-1].set_visible(True)
		else:
			self.ax0.lines[line-1].set_visible(False)
		self.fig.canvas.draw()


	def e_add_gyro(self,var,line):
		if var.get():
			self.ax1.lines[line-1].set_visible(True)
		else:
			self.ax1.lines[line-1].set_visible(False)
		self.fig.canvas.draw()




	######## altre funzioni

	def select_port(self):
		SERIAL_PORT = self.tree.set(self.tree.selection(), 'PORTA') or 'None'
		#print ("Selezionata porta " + SERIAL_PORT)
		return SERIAL_PORT


	def non_connesso(self):
		self.label_connessione['text'] = self.lbl_stato_conn_off
		self.Button_connetti.config(state = "enabled")
		self.Button_disconnetti.config(state = "disabled")
		self.Button_START.config(state = "disabled")
		self.Button_STOP.config(state = "disabled")


	def connesso(self):
		self.Button_connetti.config(state = "disabled")
		self.Button_disconnetti.config(state = "enabled")
		self.Button_START.config(state = "enabled")
		self.Button_STOP.config(state = "disabled")


	def read_from_port(self,event):
		while True:
			event.wait()
			self.LINE = self.SERIAL_SER.ser.read(self.N_BYTE_RX)
			#print(self.LINE)
			THREAD_event_graph.set()


	def update_grafico(self,event):
		while True:
			event.clear()
			event.wait()
			# per test
			#self.LINE = b"#F79CF25DFAD11F90FA504420FFA1FFCEFFB6\r"
			#print(self.LINE)
			# seleziona la stringa, escluso i 2 marker '#' e '\r'
			temp = self.LINE[1:37]
			#print(temp.decode())
			# -> F79CF25DFAD11F90FA504420FFA1FFCEFFB6
			data_buff = re.findall("....",temp.decode())
			#print(data_buff)
			# -> ['F79C', 'F25D', 'FAD1', '1F90', 'FA50', '4420', 'FFA1', 'FFCE', 'FFB6']
			try:
				# note: i dati del magnetometro non servono,
				# nel caso sostituirli con quelli del gyro o dell'acc

				# gyroscopio
				# GYRO = (REG) / SENSITIVITY [mdps]
				self.gyro_buff = np.fromiter( (int(x,16) for x in data_buff[0:3]), dtype=np.int16)
				self.gyro_buff = np.round(self.gyro_buff * self.sens_gyro / 1000,3)
				#print(self.gyro_buff)

				# accelerometro
				# ACC = (1/SENSITIVITY)* (REG)/16 (12 bit rappresentation) [mg]
				self.acc_buff = np.fromiter( (int(x,16) for x in data_buff[3:6]), dtype=np.int16)
				self.acc_buff = np.round(self.acc_buff/self.sens_acc,1)
				
				# magnetometro
				# MAG = (REG) / SENSITIVITY
				# diviso 1000 per [mgauss]
				#self.mag_buff = np.fromiter( int(x,16) for x in data_buff[6:9]), dtype=np.int16)
				#self.mag_buff = np.round(self.mag_buff*1000/self.sens_mag,3)
				
				#print(self.acc_buff)
				# -> [  505.   -91.  1090.]
				# -> [-122.743 -199.486  -75.829]
			except:
				pass
			# np.hstack -> nuovo buffer con unione di 2 buffer in orizz.
			str_data = np.hstack((self.acc_buff,self.gyro_buff))
			#print(str_data)
			# -> [  505.   -91.  1090.  -122.743 -199.486  -75.829]
			# plot delle linee
			self.plotta(str_data)
			# plot dei valori nelle label
			for (lbl,val) in zip(self.label_text_val,str_data):
				lbl.set(str(val))
			self.fig.canvas.draw()


	def plotta(self,new_string):
		try:
			# graph 
			# np.insert -> aggiunge una colonna a dx alla matrice
			self.dataplot = np.insert(self.dataplot,self.maxLen,new_string,axis=1)
			# np.delete -> elimina la prima colonna a sx, riporta la matrice 
			self.dataplot = np.delete(self.dataplot,0,axis=1)
		except:
			#print("errore qui")
			pass
		#print(self.dataplot)
		#[[    0.        0.        0.        0.        0.      505.   ]
		# [    0.        0.        0.        0.        0.      -91.   ]
		# [    0.        0.        0.        0.        0.     1090.   ]
		# [    0.        0.        0.        0.        0.     -122.743]
		# [    0.        0.        0.        0.        0.     -199.486]
		# [    0.        0.        0.        0.        0.      -75.829]]
		# seleziona dalla matrice una riga alla volta, con n elementi(self.x_point) da sx
		for i,line in enumerate(self.ax0.lines):
			#print(self.dataplot[i,-self.x_point:])
			# ciclo ->0 -> [  0.   0.   0.   0.   0. 505.]
			# ciclo ->1 -> [  0.   0.   0.   0.   0. -91.]
			# ciclo ->2 -> [  0.   0.   0.   0.   0. 1090.]
			line.set_data( range(self.x_point) ,self.dataplot[i,-self.x_point:])
		for i,line in enumerate(self.ax1.lines):
			#print(self.dataplot[i+3,-self.x_point:])
			# ciclo ->0 -> [  0.   0.   0.   0.   0. -122.743]
			# ciclo ->1 -> [  0.   0.   0.   0.   0. -199.486]
			# ciclo ->2 -> [  0.   0.   0.   0.   0. -75.829]
			line.set_data( range(self.x_point) ,self.dataplot[i+3,-self.x_point:])




	def reset_graph(self):
		# grafico con punti da x=0 a x=(self.maxLen-1)
		for i,line in enumerate(self.ax0.lines):
			line.set_visible(True)
			line.set_data(range(self.maxLen),self.dataplot[i])
		for i,line in enumerate(self.ax1.lines):
			line.set_visible(True)
			line.set_data(range(self.maxLen),self.dataplot[i])
		for check_acc,check_gyro in zip(self.array_check_acc,self.array_check_gyro):
			check_acc.set(True)
			check_gyro.set(True)


	def close_window(self):
		#print("in chiusura programma")
		self.window.quit()
		self.window.destroy()


if __name__ == "__main__":
	MyApp = App()

	THREAD_event_serial = threading.Event()
	THREAD_event_serial.clear()

	THREAD_event_graph = threading.Event()
	THREAD_event_graph.clear()

	THREAD_serial = Thread(target=MyApp.read_from_port, args=(THREAD_event_serial,))
	THREAD_serial.daemon = True
	THREAD_serial.start()

	THREAD_graph = Thread(target=MyApp.update_grafico, args=(THREAD_event_graph,))
	THREAD_graph.daemon = True
	THREAD_graph.start()

	Tk.mainloop()
	#print("exit program")