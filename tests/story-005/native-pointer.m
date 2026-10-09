// SPDX-License-Identifier: GPL-2.0-or-later
// Development-only persistent pointer probe. Cam authorized native interaction
// outside Sky for autonomous hover validation on 2026-10-04.
#import <AppKit/AppKit.h>
#import <ApplicationServices/ApplicationServices.h>
static id Attribute(AXUIElementRef element, CFStringRef key) {
    CFTypeRef value=NULL; if(AXUIElementCopyAttributeValue(element,key,&value)!=kAXErrorSuccess) return nil;
    return CFBridgingRelease(value);
}
static void Sliders(AXUIElementRef element, int depth) {
    if(depth>10)return;
    if([Attribute(element,kAXRoleAttribute) isEqualToString:(__bridge NSString *)kAXSliderRole]) {
        CGPoint position=CGPointZero;CGSize size=CGSizeZero;
        id p=Attribute(element,kAXPositionAttribute),s=Attribute(element,kAXSizeAttribute);
        if(p)AXValueGetValue((__bridge AXValueRef)p,kAXValueCGPointType,&position);
        if(s)AXValueGetValue((__bridge AXValueRef)s,kAXValueCGSizeType,&size);
        printf("slider %.3f %.3f %.3f %.3f value %s title %s\n",position.x,position.y,size.width,size.height,
            [[Attribute(element,kAXValueAttribute) description] UTF8String] ?: "",[Attribute(element,kAXTitleAttribute) UTF8String] ?: "");
    }
    for(id child in Attribute(element,kAXChildrenAttribute))Sliders((__bridge AXUIElementRef)child,depth+1);
}
static void Tree(AXUIElementRef element, int depth) {
    if(depth>12)return;
    NSDictionary *row=@{@"depth":@(depth),@"role":Attribute(element,kAXRoleAttribute)?:@"",
        @"title":Attribute(element,kAXTitleAttribute)?:@"",@"help":Attribute(element,kAXHelpAttribute)?:@"",
        @"description":Attribute(element,kAXDescriptionAttribute)?:@"",
        @"value":[Attribute(element,kAXValueAttribute) description]?:@""};
    NSData *json=[NSJSONSerialization dataWithJSONObject:row options:0 error:nil];
    puts([[NSString alloc]initWithData:json encoding:NSUTF8StringEncoding].UTF8String);
    for(id child in Attribute(element,kAXChildrenAttribute))Tree((__bridge AXUIElementRef)child,depth+1);
}
static void FindButtons(AXUIElementRef element, NSString *name, int depth, NSMutableArray *matches) {
    if(depth>12)return;
    NSString *role=Attribute(element,kAXRoleAttribute);
    if(([role isEqualToString:(__bridge NSString *)kAXButtonRole] || [role isEqualToString:@"AXCheckBox"]) &&
       ([Attribute(element,kAXTitleAttribute) isEqualToString:name] ||
        [Attribute(element,kAXDescriptionAttribute) isEqualToString:name]))
        [matches addObject:(__bridge id)element];
    for(id child in Attribute(element,kAXChildrenAttribute))FindButtons((__bridge AXUIElementRef)child,name,depth+1,matches);
}
int main(int argc, const char **argv) { @autoreleasepool {
    if (argc < 3) { fprintf(stderr,"usage: native-pointer inspect|move PID [global-X global-Y]\n"); return 2; }
    pid_t pid = atoi(argv[2]);
    NSRunningApplication *app = [NSRunningApplication runningApplicationWithProcessIdentifier:pid];
    // Exact domain AND app path; never infer ownership from VLC's display name.
    NSString *repo = [[NSFileManager defaultManager] currentDirectoryPath];
    NSDictionary *ownedPaths = @{
        @"org.videolan.vlc.story005.nativebaseline.discriminator006": [repo stringByAppendingPathComponent:@"work/story005-native-baseline/VLCStory005Baseline006.app"],
        @"org.videolan.vlc.story005.nativecandidate": [repo stringByAppendingPathComponent:@"work/story005-master-candidate/VLC.app"],
        @"org.videolan.vlc.story005.nativebaseline.discriminator012": [repo stringByAppendingPathComponent:@"work/story005-native-baseline/VLCStory005Baseline012.app"],
        @"org.videolan.vlc.story005.nativecandidate.discriminator011": [repo stringByAppendingPathComponent:@"work/story005-native-candidate/VLCStory005Candidate011.app"],
        @"org.videolan.vlc.story005.nativecandidate.discriminator007": [repo stringByAppendingPathComponent:@"work/story005-native-candidate/VLCStory005Candidate007.app"]
    };
    NSString *expectedPath = ownedPaths[app.bundleIdentifier ?: @""];
    if (!expectedPath || ![app.bundleURL.path isEqualToString:expectedPath]) {
        fprintf(stderr,"Only an exact isolated VLC domain/path may be targeted\n"); return 2;
    }
    if (!strcmp(argv[1],"activate")) {
        BOOL ok=[app activateWithOptions:0];
        printf("{\"activated\":%s}\n",ok?"true":"false");return ok?0:1;
    }
    if (!strcmp(argv[1],"focus")) {
        AXUIElementRef target=AXUIElementCreateApplication(pid);
        id window=Attribute(target,kAXFocusedWindowAttribute);
        id element=Attribute(target,kAXFocusedUIElementAttribute);
        CGPoint point=CGPointZero;CGSize size=CGSizeZero;
        id p=window?Attribute((__bridge AXUIElementRef)window,kAXPositionAttribute):nil;
        id s=window?Attribute((__bridge AXUIElementRef)window,kAXSizeAttribute):nil;
        if(p)AXValueGetValue((__bridge AXValueRef)p,kAXValueCGPointType,&point);
        if(s)AXValueGetValue((__bridge AXValueRef)s,kAXValueCGSizeType,&size);
        NSDictionary *result=@{@"app_active":@(app.active),@"window_position":@[@(point.x),@(point.y)],@"window_size":@[@(size.width),@(size.height)],@"focused_role":element?Attribute((__bridge AXUIElementRef)element,kAXRoleAttribute)?:@"":@""};
        NSData *json=[NSJSONSerialization dataWithJSONObject:result options:0 error:nil];
        puts([[NSString alloc]initWithData:json encoding:NSUTF8StringEncoding].UTF8String);CFRelease(target);return 0;
    }
    if (!strcmp(argv[1],"place") && argc==7) {
        double x=atof(argv[3]),y=atof(argv[4]),w=atof(argv[5]),h=atof(argv[6]);
        if(x<0 || y<33 || w<604 || h<360 || x+w>1728 || y+h>1117)return 2;
        AXUIElementRef target=AXUIElementCreateApplication(pid);
        id window=Attribute(target,kAXFocusedWindowAttribute);
        CGPoint point=CGPointMake(x,y);CGSize size=CGSizeMake(w,h);
        AXValueRef pv=AXValueCreate(kAXValueCGPointType,&point),sv=AXValueCreate(kAXValueCGSizeType,&size);
        AXError a=window?AXUIElementSetAttributeValue((__bridge AXUIElementRef)window,kAXSizeAttribute,sv):kAXErrorFailure;
        AXError b=window?AXUIElementSetAttributeValue((__bridge AXUIElementRef)window,kAXPositionAttribute,pv):kAXErrorFailure;
        CFRelease(pv);CFRelease(sv);CFRelease(target);
        printf("{\"size_error\":%d,\"position_error\":%d}\n",a,b);return a==kAXErrorSuccess && b==kAXErrorSuccess?0:1;
    }
    if (!strcmp(argv[1],"resize") && argc==5) {
        double w=atof(argv[3]),h=atof(argv[4]); if(w<604 || h<360 || w>1728 || h>1117)return 2;
        AXUIElementRef target=AXUIElementCreateApplication(pid);
        id window=Attribute(target,kAXFocusedWindowAttribute);CGSize size=CGSizeMake(w,h);
        AXValueRef value=AXValueCreate(kAXValueCGSizeType,&size);
        AXError result=window?AXUIElementSetAttributeValue((__bridge AXUIElementRef)window,kAXSizeAttribute,value):kAXErrorFailure;
        CFRelease(value);CFRelease(target);printf("{\"ax_error\":%d}\n",result);return result==kAXErrorSuccess?0:1;
    }
    if (!strcmp(argv[1],"press") && (argc==4 || argc==5)) {
        AXUIElementRef target=AXUIElementCreateApplication(pid);
        NSMutableArray *matches=[NSMutableArray array];
        NSArray *windows=Attribute(target,kAXWindowsAttribute);
        if(argc==5) {
            NSInteger index=atoi(argv[4]);
            if(index<0 || index>=(NSInteger)windows.count) { CFRelease(target);return 2; }
            windows=@[windows[index]];
        }
        for(id window in windows)FindButtons((__bridge AXUIElementRef)window,[NSString stringWithUTF8String:argv[3]],0,matches);
        AXError result=matches.count==1 ? AXUIElementPerformAction((__bridge AXUIElementRef)matches.firstObject,kAXPressAction) : kAXErrorFailure;
        CFRelease(target);printf("{\"matches\":%lu,\"ax_error\":%d}\n",(unsigned long)matches.count,result);return result==kAXErrorSuccess?0:1;
    }
    if (!strcmp(argv[1],"tree")) {
        AXUIElementRef target=AXUIElementCreateApplication(pid);
        for(id window in Attribute(target,kAXWindowsAttribute))Tree((__bridge AXUIElementRef)window,0);
        CFRelease(target);return 0;
    }
    if (!strcmp(argv[1],"ax")) {
        AXUIElementRef target=AXUIElementCreateApplication(pid);
        NSUInteger index=0;
        for(id window in Attribute(target,kAXWindowsAttribute)) {
            printf("window_index %lu\n",(unsigned long)index++);
            Sliders((__bridge AXUIElementRef)window,0);
        }
        CFRelease(target);return 0;
    }
    if (!strcmp(argv[1],"close") && argc==4) {
        AXUIElementRef target=AXUIElementCreateApplication(pid);
        NSArray *windows=Attribute(target,kAXWindowsAttribute);NSInteger index=atoi(argv[3]);
        if(index<0 || index>=(NSInteger)windows.count) { CFRelease(target);return 2; }
        id button=Attribute((__bridge AXUIElementRef)windows[index],kAXCloseButtonAttribute);
        AXError result=button?AXUIElementPerformAction((__bridge AXUIElementRef)button,kAXPressAction):kAXErrorFailure;
        CFRelease(target);printf("{\"ax_error\":%d}\n",result);return result==kAXErrorSuccess?0:1;
    }
    if (!strcmp(argv[1],"raise") && argc==4) {
        AXUIElementRef target=AXUIElementCreateApplication(pid);
        NSArray *windows=Attribute(target,kAXWindowsAttribute);NSInteger index=atoi(argv[3]);
        if(index<0 || index>=(NSInteger)windows.count) { CFRelease(target);return 2; }
        AXError result=AXUIElementPerformAction((__bridge AXUIElementRef)windows[index],kAXRaiseAction);
        CFRelease(target);printf("{\"ax_error\":%d}\n",result);return result==kAXErrorSuccess?0:1;
    }
    if (!strcmp(argv[1],"inspect")) {
        NSArray *windows = CFBridgingRelease(CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly,kCGNullWindowID));
        NSMutableArray *owned = [NSMutableArray array];
        for (NSDictionary *w in windows) if ([w[(__bridge NSString *)kCGWindowOwnerPID] intValue] == pid)
            [owned addObject:@{@"id":w[(__bridge NSString *)kCGWindowNumber],@"bounds":w[(__bridge NSString *)kCGWindowBounds],@"layer":w[(__bridge NSString *)kCGWindowLayer],@"name":w[(__bridge NSString *)kCGWindowName] ?: @""}];
        NSData *json=[NSJSONSerialization dataWithJSONObject:owned options:0 error:nil];
        puts([[NSString alloc] initWithData:json encoding:NSUTF8StringEncoding].UTF8String);return 0;
    }
    BOOL click = !strcmp(argv[1],"click");
    if ((!click && strcmp(argv[1],"move")) || argc != 5) return 2;
    double x=atof(argv[3]),y=atof(argv[4]); if (!isfinite(x)||!isfinite(y)) return 2;
    if (click) {
        // Hit-test ownership: transparent system overlay bounds cover the screen
        // even where actual mouse events pass through them.
        AXUIElementRef system=AXUIElementCreateSystemWide(),hit=NULL;pid_t hitPID=0;
        AXError result=AXUIElementCopyElementAtPosition(system,x,y,&hit);
        if(result==kAXErrorSuccess && hit)AXUIElementGetPid(hit,&hitPID);
        if(hit)CFRelease(hit);CFRelease(system);
        if(result!=kAXErrorSuccess || hitPID!=pid) {
            fprintf(stderr,"Click hit-test must belong to target PID (error %d, PID %d)\n",result,hitPID);return 1;
        }
    }
    // Hover must not activate the app or change its fullscreen/key-window state.
    CGPoint point=CGPointMake(x,y);
    CGError err=CGWarpMouseCursorPosition(point);
    CGEventRef event=CGEventCreateMouseEvent(NULL,kCGEventMouseMoved,point,kCGMouseButtonLeft);
    if (!event || err!=kCGErrorSuccess) return 1;
    CGEventPost(kCGHIDEventTap,event);CFRelease(event);usleep(100000);
    if(click) {
        for(int i=0;i<2;i++) {
            CGEventRef button=CGEventCreateMouseEvent(NULL,i?kCGEventLeftMouseUp:kCGEventLeftMouseDown,point,kCGMouseButtonLeft);
            if(!button)return 1;
            CGEventSetIntegerValueField(button,kCGMouseEventClickState,1);
            CGEventPost(kCGHIDEventTap,button);CFRelease(button);usleep(50000);
        }
    }
    CGEventRef current=CGEventCreate(NULL);CGPoint actual=CGEventGetLocation(current);CFRelease(current);
    printf("{\"requested\":[%.3f,%.3f],\"pointer\":[%.3f,%.3f]}\n",x,y,actual.x,actual.y);
    return hypot(actual.x-x,actual.y-y)<1.0 ? 0 : 1;
} }
