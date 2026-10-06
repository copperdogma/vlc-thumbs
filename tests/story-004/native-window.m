// SPDX-License-Identifier: GPL-2.0-or-later
// Owned-test window selection; raises exactly one AX window of the supplied PID.
#import <Cocoa/Cocoa.h>
#import <ApplicationServices/ApplicationServices.h>
#include <stdio.h>
int main(int argc,const char **argv){@autoreleasepool {
 if(argc!=3)return 2;
 pid_t pid=(pid_t)atoi(argv[1]);NSInteger index=atoi(argv[2]);
 if(pid<=0||index<0)return 2;
 AXUIElementRef app=AXUIElementCreateApplication(pid);CFTypeRef list=NULL;
 AXError error=AXUIElementCopyAttributeValue(app,kAXWindowsAttribute,&list);
 if(error!=kAXErrorSuccess||!list||CFGetTypeID(list)!=CFArrayGetTypeID()||index>=CFArrayGetCount(list)){if(list)CFRelease(list);CFRelease(app);return 3;}
 AXUIElementRef window=(AXUIElementRef)CFArrayGetValueAtIndex(list,index);
 error=AXUIElementPerformAction(window,kAXRaiseAction);
 printf("{\"pid\":%d,\"window_index\":%ld,\"raise_error\":%d}\n",pid,(long)index,error);
 CFRelease(list);CFRelease(app);return error==kAXErrorSuccess?0:1;
}}
