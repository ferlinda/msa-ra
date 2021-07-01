import random
from matplotlib import pyplot as plt
from collections import Counter 
import tkinter as tk

class Device:

    def __init__(self, id, channel, range_backoff, backoff_timer, total_transmission, status, success_slot):
        self.id = id
        self.channel = channel
        self.range_backoff = range_backoff
        self.backoff_timer = backoff_timer
        self.total_transmission = total_transmission
        self.status = status
        self.success_slot = success_slot

    def __str__(self):
        return "ID=%s,Channel=%s,Back off Range=%s,Back off timer=%s,Transmission=%s,Status=%s,Slot=%s" % (self.id,self.channel,self.range_backoff,self.backoff_timer,self.total_transmission,self.status,self.success_slot)

def print_devices(device_list):
    for device in device_list:
        print(str(device))
    print('--------------------------------------------')

def initialization(M):
    device_list=[]
    for device_id in range(0,M):
        id=device_id+1
        channel=None
        status=None
        total_transmission=0
        range_backoff=None
        backoff_timer=0
        status="will_transmit"
        success_slot=None
        device_list.append(Device(id, channel, range_backoff, backoff_timer, total_transmission, status, success_slot))
    return device_list

# print_devices(initialization(100))

def send_channel_request(device_list,R):
    # Device that previously will transmit, transmit at this phase of ts
    for device in device_list:
        if device.status=="will_transmit":
            device.channel=random.randint(1,R)
            device.total_transmission+=1
            device.status="transmitted"
    return device_list

def generate_channel_list(device_list):
    # Generate list of picked channel
    picked_channel=[]
    for device in device_list:
        if device.status=="transmitted":
            picked_channel.append(device.channel)
    return picked_channel

def check_collision(device_list, picked_channel, slot,max_transmission):
    for device in device_list:
        if device.status=="transmitted":
            not_collide=picked_channel.count(device.channel)
            if not_collide==1:
                device.status="success"
                device.success_slot=slot
            else:
                device.status="collided"
                if device.total_transmission==max_transmission:
                    device.status="failed"
    return device_list

def set_collided_backoff(device_list,backoff_window):
    for device in device_list:
        if device.status=="collided":
            if device.total_transmission==1:
                device.range_backoff=random.randint(1,backoff_window)
            else:
                device.range_backoff=random.randint(1,device.range_backoff+1)
            device.backoff_timer=device.range_backoff
    return device_list

def set_backoff_timer(device_list):
    for device in device_list:
        if device.status=="collided" or device.status=="wait":
            device.backoff_timer-=1
            if device.backoff_timer==0:
                device.status="will_transmit"
            else: 
                device.status="wait"
    return device_list

def complete_transmit_check(device_list, M):
    sum_success=0
    for device in device_list:
        if device.status=="success" or device.status=="failed":
            sum_success+=1
    if sum_success==M:
        return 1
    else:
        return 0

def transmitting_devices_check(device_list,slot):
    sum_success=0
    sum_transmit=0
    for device in device_list:
        if device.slot==slot:
            sum_success+=1
            sum_transmit+=1
            if device.status=="collided":
                sum_transmit+=1
    avg_success_slot=sum_success/sum_transmit
    return avg_success_slot

def count_success_in_slot(device_list, slot):
    sum_success=0
    for device in device_list:
        if device.status=="success" and device.success_slot==slot:
            sum_success+=1
    return sum_success

def count_sucprob(device_list,M):
    sum_success=0
    for device in device_list:
        if device.status=="success":
            sum_success+=1
    avg_success=(sum_success/M)*100
    return avg_success

def start_sim(total_channel,total_machine,max_transmission,backoff_window,range_check,repetition):
    M=1
    backoff_window=backoff_window
    max_transmission=max_transmission
    success_prob_list_each=[]
    num_of_dev=[]
    avg_success_list=[]

    ts_list=[]
    avg_delay=[]
    avg_delay_list=[]

    success_list=[]
    list_success_slot=[]
    slot_list=[]
    list_transmission_slot=[]


    while M<total_machine+1:
        rep=0
        while rep<repetition:
            slot=1
            device_list=initialization(M)
            while True:
                breakpoint=complete_transmit_check(device_list,M)
                if breakpoint==1:
                    break
                device_list=send_channel_request(device_list, total_channel)
                picked_channel=generate_channel_list(device_list)
                device_list=check_collision(device_list, picked_channel, slot,max_transmission)
                if M==range_check:
                    sum_success=count_success_in_slot(device_list, slot)
                    try:
                        list_success_slot[slot-1]
                    except IndexError:
                        list_success_slot.append(0)
                    try:
                        list_transmission_slot[slot-1]
                    except IndexError:
                        list_transmission_slot.append(0)
                    try:
                        slot_list[slot-1]
                    except IndexError:
                        slot_list.append(slot)

                    list_success_slot[slot-1]+=sum_success
                    total_transmission=len(picked_channel)
                    list_transmission_slot[slot-1]+=total_transmission
                # Setting backoff
                set_collided_backoff(device_list,backoff_window)
                set_backoff_timer(device_list)
                # For counting delay
                ts_list.append(slot)
                # Next slot
                slot+=1
            # Count success probability
            success_prob=count_sucprob(device_list,M)
            success_prob_list_each.append(success_prob)
            if rep==0:
                avg_delay_list.append(0)
            avg_delay_list[M-1]+=slot-2
            # Next repetition
            rep+=1
        # Count average success probability
        num_of_dev.append(M)
        avg_success=sum(success_prob_list_each)/len(success_prob_list_each)
        avg_success_list.append(avg_success)
        success_prob_list_each=[]

        i=0
        for j in list_success_slot:
            try:
                list_success_slot[i]=j/rep
            except ZeroDivisionError:
                list_success_slot[i]=0
            i+=1

        
        i=0

        for j in list_transmission_slot:
            try:
                list_transmission_slot[i]=j/rep
            except ZeroDivisionError:
                list_transmission_slot[i]=0
            i+=1
        ts_list=[]
        # Next device
        M+=1
    i=0
    for j in avg_delay_list:
        try:
            avg_delay_list[i]=j/rep
        except ZeroDivisionError:
            avg_delay_list[i]=0
        i+=1
    return(num_of_dev,avg_success_list,avg_delay_list,slot_list,list_success_slot,list_transmission_slot)

def cm_to_inch(value):
    return value/2.54

def main():
    print("RA-MSA\n----------------------------------\nChoose parameter:\n1. Channel\n2. Backoff window\n3. Maximum wransmission\n----------------------------------\nYour choice: ")
    choice=int(input())
    print("----------------------------------")
    print("Machine range limit: ")
    MRL=int(input())
    print("Total machine for transmission check: ")
    TM=int(input())
    print("Number of repetition: ")
    R=int(input())
    if choice==1:
        print("Backoff window: ")
        BW=int(input())
        print("Maximum transmission: ")
        MT=int(input())
        print("Channel (A): ")
        C_one=int(input())
        print("Channel (B): ")
        C_two=int(input())
        print("Channel (C): ")
        C_three=int(input())
        print("Channel (D): ")
        C_four=int(input())
        num_of_dev1,avg_success_list1,avg_delay_list1,slot_list1,list_success_slot1,list_transmission_slot1=start_sim(C_one,MRL,MT,BW,TM,R)
        num_of_dev2,avg_success_list2,avg_delay_list2,slot_list2,list_success_slot2,list_transmission_slot2=start_sim(C_two,MRL,MT,BW,TM,R)
        num_of_dev3,avg_success_list3,avg_delay_list3,slot_list3,list_success_slot3,list_transmission_slot3=start_sim(C_three,MRL,MT,BW,TM,R)
        num_of_dev4,avg_success_list4,avg_delay_list4,slot_list4,list_success_slot4,list_transmission_slot4=start_sim(C_four,MRL,MT,BW,TM,R)
    elif choice==2:
        print("Channel: ")
        C=int(input())
        print("Maximum transmission: ")
        MT=int(input())
        print("Backoff window (A): ")
        BW_one=int(input())
        print("Backoff window (B): ")
        BW_two=int(input())
        print("Backoff window (C): ")
        BW_three=int(input())
        print("Backoff window (D): ")
        BW_four=int(input())
        num_of_dev1,avg_success_list1,avg_delay_list1,slot_list1,list_success_slot1,list_transmission_slot1=start_sim(C,MRL,MT,BW_one,TM,R)
        num_of_dev2,avg_success_list2,avg_delay_list2,slot_list2,list_success_slot2,list_transmission_slot2=start_sim(C,MRL,MT,BW_two,TM,R)
        num_of_dev3,avg_success_list3,avg_delay_list3,slot_list3,list_success_slot3,list_transmission_slot3=start_sim(C,MRL,MT,BW_three,TM,R)
        num_of_dev4,avg_success_list4,avg_delay_list4,slot_list4,list_success_slot4,list_transmission_slot4=start_sim(C,MRL,MT,BW_four,TM,R)
    elif choice==3:
        print("Channel: ")
        C=int(input())
        print("Backoff window: ")
        BW=int(input())
        print("Maximum transmission (A): ")
        MT_one=int(input())
        print("Maximum transmission (B): ")
        MT_two=int(input())
        print("Maximum transmission (C): ")
        MT_three=int(input())
        print("Maximum transmission (D): ")
        MT_four=int(input())
        num_of_dev1,avg_success_list1,avg_delay_list1,slot_list1,list_success_slot1,list_transmission_slot1=start_sim(C,MRL,MT_one,BW,TM,R)
        num_of_dev2,avg_success_list2,avg_delay_list2,slot_list2,list_success_slot2,list_transmission_slot2=start_sim(C,MRL,MT_two,BW,TM,R)
        num_of_dev3,avg_success_list3,avg_delay_list3,slot_list3,list_success_slot3,list_transmission_slot3=start_sim(C,MRL,MT_three,BW,TM,R)
        num_of_dev4,avg_success_list4,avg_delay_list4,slot_list4,list_success_slot4,list_transmission_slot4=start_sim(C,MRL,MT_four,BW,TM,R)
    else:
        print("Wrong choice.")
        exit()
    print(num_of_dev1,avg_success_list1,avg_delay_list1,slot_list1,list_success_slot1,list_transmission_slot1)
    print(num_of_dev2,avg_success_list2,avg_delay_list2,slot_list2,list_success_slot2,list_transmission_slot2)
    print(num_of_dev3,avg_success_list3,avg_delay_list3,slot_list3,list_success_slot3,list_transmission_slot3)
    print(num_of_dev4,avg_success_list4,avg_delay_list4,slot_list4,list_success_slot4,list_transmission_slot4)
    fig, axs = plt.subplots(nrows=2,ncols=2)
    axs[0, 0].plot(num_of_dev1, avg_success_list1,label='A')
    axs[0, 0].plot(num_of_dev2, avg_success_list2,label='B')
    axs[0, 0].plot(num_of_dev3, avg_success_list3,label='C')
    axs[0, 0].plot(num_of_dev4, avg_success_list4,label='D')
    axs[0, 0].set_title("Average success probability")
    axs[0, 0].set(xlabel='Total device',ylabel='Success probability')
    axs[0, 0].legend()
    axs[0, 1].plot(num_of_dev1, avg_delay_list1,label='A')
    axs[0, 1].plot(num_of_dev2, avg_delay_list2,label='B')
    axs[0, 1].plot(num_of_dev3, avg_delay_list3,label='C')
    axs[0, 1].plot(num_of_dev4, avg_delay_list4,label='D')
    axs[0, 1].set_title("Average delay")
    axs[0, 1].set(xlabel='Total device',ylabel='Delay')
    axs[0, 1].legend()
    axs[1, 0].plot(slot_list1, list_success_slot1,label='A')
    axs[1, 0].plot(slot_list2, list_success_slot2,label='B')
    axs[1, 0].plot(slot_list3, list_success_slot3,label='C')
    axs[1, 0].plot(slot_list4, list_success_slot4,label='D')
    axs[1, 0].set_title("Successful transmission at slot")
    axs[1, 0].set(xlabel='Slot',ylabel='Total successful transmission')
    axs[1, 0].legend()
    axs[1, 1].plot(slot_list1, list_transmission_slot1,label='A')
    axs[1, 1].plot(slot_list2, list_transmission_slot2,label='B')
    axs[1, 1].plot(slot_list3, list_transmission_slot3,label='C')
    axs[1, 1].plot(slot_list4, list_transmission_slot4,label='D')
    axs[1, 1].set_title("Total transmission at slot")
    axs[1, 1].set(xlabel='Slot',ylabel='Total Transmission')
    axs[1, 1].legend()
    plt.rcParams['figure.figsize'] = [cm_to_inch(50),cm_to_inch(55)]
    plt.show()


main()
