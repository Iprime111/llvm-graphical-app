; ModuleID = '/Users/ip111/Code/llvm-course/graphical-app/src/app.c'
source_filename = "/Users/ip111/Code/llvm-course/graphical-app/src/app.c"
target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx14.0.0"

; Function Attrs: nounwind optsize sspstrong uwtable(sync)
define void @app() local_unnamed_addr #0 {
entry:
  br label %for.body

for.cond.cleanup:                                 ; preds = %if.end40
  ret void

for.body:                                         ; preds = %entry, %if.end40
  %frame.089 = phi i32 [ 0, %entry ], [ %inc, %if.end40 ]
  tail call fastcc void @box(i32 noundef 0, i32 noundef 0, i32 noundef 1536, i32 noundef 768, i32 noundef -16578798) #3
  br label %for.body.i

for.body.i:                                       ; preds = %for.inc.i, %for.body
  %i.030.i = phi i32 [ 0, %for.body ], [ %inc15.i, %for.inc.i ]
  %bright.029.i = phi i32 [ 0, %for.body ], [ %bright.1.i, %for.inc.i ]
  %y.028.i = phi i32 [ 31, %for.body ], [ %y.1.i, %for.inc.i ]
  %x.027.i = phi i32 [ 73, %for.body ], [ %spec.select.i, %for.inc.i ]
  %add.i = add i32 %x.027.i, 347
  %add1.i = add i32 %y.028.i, 197
  %cmp2.i = icmp sgt i32 %add.i, 1535
  %sub.i = add nsw i32 %x.027.i, -1189
  %spec.select.i = select i1 %cmp2.i, i32 %sub.i, i32 %add.i
  %cmp3.i = icmp sgt i32 %add1.i, 767
  %sub5.i = add nsw i32 %y.028.i, -571
  %y.1.i = select i1 %cmp3.i, i32 %sub5.i, i32 %add1.i
  tail call void @simPutPixel(i32 noundef %spec.select.i, i32 noundef %y.1.i, i32 noundef -10059111) #4
  %inc.i = add i32 %bright.029.i, 1
  %cmp7.i = icmp eq i32 %inc.i, 9
  br i1 %cmp7.i, label %if.then8.i, label %for.inc.i

if.then8.i:                                       ; preds = %for.body.i
  %add9.i = add i32 %spec.select.i, 1
  %cmp10.i = icmp slt i32 %add9.i, 1536
  br i1 %cmp10.i, label %if.then11.i, label %for.inc.i

if.then11.i:                                      ; preds = %if.then8.i
  tail call void @simPutPixel(i32 noundef %add9.i, i32 noundef %y.1.i, i32 noundef -4598817) #4
  br label %for.inc.i

for.inc.i:                                        ; preds = %if.then11.i, %if.then8.i, %for.body.i
  %bright.1.i = phi i32 [ %inc.i, %for.body.i ], [ 0, %if.then11.i ], [ 0, %if.then8.i ]
  %inc15.i = add nuw nsw i32 %i.030.i, 1
  %exitcond.not.i = icmp eq i32 %inc15.i, 190
  br i1 %exitcond.not.i, label %background.exit, label %for.body.i, !llvm.loop !6

background.exit:                                  ; preds = %for.inc.i
  %cmp1 = icmp samesign ult i32 %frame.089, 38
  br i1 %cmp1, label %for.body.i61, label %for.body.i68.preheader

for.body.i68.preheader:                           ; preds = %for.cond.cleanup3.i, %background.exit
  br label %for.body.i68

for.body.i61:                                     ; preds = %background.exit, %for.cond.cleanup3.i
  %y.071.i = phi i32 [ %inc45.i, %for.cond.cleanup3.i ], [ 330, %background.exit ]
  %sub.i62 = add nsw i32 %y.071.i, -515
  %mul6.i = mul nsw i32 %sub.i62, %sub.i62
  %sub8.i = add nsw i32 %y.071.i, -530
  %mul12.i = shl i32 %sub8.i, 1
  %mul13.i = mul nsw i32 %mul12.i, %sub8.i
  %sub10.i = add nsw i32 %y.071.i, -450
  %mul18.i = mul nsw i32 %sub10.i, %sub10.i
  %invariant.op.i = sub nsw i32 13000, %mul18.i
  %cmp32.i = icmp samesign ult i32 %y.071.i, 365
  br label %for.body4.i

for.cond.cleanup3.i:                              ; preds = %cleanup.i
  %inc45.i = add nuw nsw i32 %y.071.i, 1
  %exitcond72.not.i = icmp eq i32 %inc45.i, 701
  br i1 %exitcond72.not.i, label %for.body.i68.preheader, label %for.body.i61, !llvm.loop !8

for.body4.i:                                      ; preds = %cleanup.i, %for.body.i61
  %x.069.i = phi i32 [ 583, %for.body.i61 ], [ %inc.i65, %cleanup.i ]
  %sub5.i63 = add nsw i32 %x.069.i, -768
  %mul.i = mul nsw i32 %sub5.i63, %sub5.i63
  %add.i64 = add nuw nsw i32 %mul.i, %mul6.i
  %sub7.i = add nsw i32 %x.069.i, -703
  %mul11.i = mul nsw i32 %sub7.i, %sub7.i
  %add14.i = add nsw i32 %mul11.i, %mul13.i
  %cmp15.i = icmp slt i32 %add14.i, 16000
  %sub9.i = add nsw i32 %x.069.i, -848
  %mul16.i = shl nsw i32 %sub9.i, 1
  %mul17.i = mul nsw i32 %mul16.i, %sub9.i
  %cmp20.i = icmp slt i32 %mul17.i, %invariant.op.i
  %0 = select i1 %cmp15.i, i1 true, i1 %cmp20.i
  %cmp21.i = icmp samesign ugt i32 %add.i64, 34225
  br i1 %cmp21.i, label %cleanup.i, label %if.end.i

if.end.i:                                         ; preds = %for.body4.i
  %cmp22.i = icmp samesign ult i32 %add.i64, 32401
  br i1 %cmp22.i, label %if.then23.i, label %if.end35.i

if.then23.i:                                      ; preds = %if.end.i
  %cmp24.i = icmp samesign ult i32 %x.069.i, 733
  %spec.store.select.i = select i1 %0, i32 -15192025, i32 -16311510
  %spec.store.select48.i = select i1 %0, i32 -13543870, i32 -15582382
  %color.0.i = select i1 %cmp24.i, i32 %spec.store.select.i, i32 %spec.store.select48.i
  %spec.select.i67 = select i1 %cmp32.i, i32 -10453629, i32 %color.0.i
  br label %if.end35.i

if.end35.i:                                       ; preds = %if.then23.i, %if.end.i
  %color.1.i = phi i32 [ -15052441, %if.end.i ], [ %spec.select.i67, %if.then23.i ]
  tail call void @simPutPixel(i32 noundef %x.069.i, i32 noundef %y.071.i, i32 noundef %color.1.i) #4
  br label %cleanup.i

cleanup.i:                                        ; preds = %if.end35.i, %for.body4.i
  %inc.i65 = add nuw nsw i32 %x.069.i, 1
  %exitcond.not.i66 = icmp eq i32 %inc.i65, 954
  br i1 %exitcond.not.i66, label %for.cond.cleanup3.i, label %for.body4.i, !llvm.loop !9

for.cond.cleanup.i:                               ; preds = %for.body.i68
  tail call fastcc void @box(i32 noundef 540, i32 noundef 111, i32 noundef 1000, i32 noundef 114, i32 noundef -6323886) #3
  tail call fastcc void @box(i32 noundef 540, i32 noundef 160, i32 noundef 1000, i32 noundef 163, i32 noundef -6323886) #3
  tail call fastcc void @box(i32 noundef 540, i32 noundef 172, i32 noundef 1000, i32 noundef 175, i32 noundef -11116182) #3
  tail call fastcc void @box(i32 noundef 505, i32 noundef 111, i32 noundef 540, i32 noundef 201, i32 noundef -14998225) #3
  tail call fastcc void @box(i32 noundef 480, i32 noundef 127, i32 noundef 505, i32 noundef 189, i32 noundef -12147529) #3
  tail call fastcc void @box(i32 noundef 590, i32 noundef 83, i32 noundef 720, i32 noundef 111, i32 noundef -14998225) #3
  tail call fastcc void @box(i32 noundef 610, i32 noundef 49, i32 noundef 654, i32 noundef 111, i32 noundef -11116182) #3
  tail call fastcc void @box(i32 noundef 627, i32 noundef 8, i32 noundef 637, i32 noundef 49, i32 noundef -4021910) #3
  tail call fastcc void @box(i32 noundef 668, i32 noundef 67, i32 noundef 702, i32 noundef 111, i32 noundef -11116182) #3
  tail call fastcc void @box(i32 noundef 681, i32 noundef 24, i32 noundef 687, i32 noundef 67, i32 noundef -4021910) #3
  tail call fastcc void @box(i32 noundef 613, i32 noundef 77, i32 noundef 623, i32 noundef 93, i32 noundef -6148309) #3
  tail call fastcc void @box(i32 noundef 678, i32 noundef 83, i32 noundef 688, i32 noundef 108, i32 noundef -6148309) #3
  br label %for.body8.i

for.body.i68:                                     ; preds = %for.body.i68.preheader, %for.body.i68
  %y.029.i = phi i32 [ %add4.i, %for.body.i68 ], [ 111, %for.body.i68.preheader ]
  %sub.i69 = add nsw i32 %y.029.i, -111
  %cmp1.i = icmp samesign ugt i32 %y.029.i, 156
  %sub2.i = sub nuw nsw i32 201, %y.029.i
  %spec.select.i70 = select i1 %cmp1.i, i32 %sub2.i, i32 %sub.i69
  %mul.i71 = shl nsw i32 %spec.select.i70, 1
  %add.i72 = add nsw i32 %mul.i71, 1000
  %add3.i = add nsw i32 %mul.i71, 1001
  %add4.i = add nuw nsw i32 %y.029.i, 1
  tail call fastcc void @box(i32 noundef 540, i32 noundef %y.029.i, i32 noundef %add3.i, i32 noundef %add4.i, i32 noundef -13616315) #3
  tail call void @simPutPixel(i32 noundef %add.i72, i32 noundef %y.029.i, i32 noundef -6323886) #4
  %exitcond.not.i73 = icmp eq i32 %add4.i, 202
  br i1 %exitcond.not.i73, label %for.cond.cleanup.i, label %for.body.i68, !llvm.loop !10

for.body8.i:                                      ; preds = %for.body8.i, %for.cond.cleanup.i
  %x.030.i = phi i32 [ 595, %for.cond.cleanup.i ], [ %add14.i75, %for.body8.i ]
  %add9.i74 = add nuw nsw i32 %x.030.i, 35
  tail call fastcc void @box(i32 noundef %x.030.i, i32 noundef 139, i32 noundef %add9.i74, i32 noundef 160, i32 noundef -14340811) #3
  %add10.i = add nuw nsw i32 %x.030.i, 3
  %add12.i = add nuw nsw i32 %x.030.i, 13
  tail call fastcc void @box(i32 noundef %add10.i, i32 noundef 142, i32 noundef %add12.i, i32 noundef 157, i32 noundef -6148309) #3
  %add14.i75 = add nuw nsw i32 %x.030.i, 56
  %cmp6.i = icmp samesign ult i32 %x.030.i, 924
  br i1 %cmp6.i, label %for.body8.i, label %ship.exit, !llvm.loop !11

ship.exit:                                        ; preds = %for.body8.i
  tail call fastcc void @box(i32 noundef 625, i32 noundef 201, i32 noundef 870, i32 noundef 219, i32 noundef -14998225) #3
  tail call fastcc void @box(i32 noundef 755, i32 noundef 219, i32 noundef 781, i32 noundef 241, i32 noundef -11116182) #3
  tail call fastcc void @box(i32 noundef 758, i32 noundef 238, i32 noundef 778, i32 noundef 244, i32 noundef -6148309) #3
  tail call fastcc void @box(i32 noundef 1090, i32 noundef 156, i32 noundef 1117, i32 noundef 159, i32 noundef -14340811) #3
  %1 = add nsw i32 %frame.089, -6
  %or.cond = icmp ult i32 %1, 4
  br i1 %or.cond, label %if.end5.thread, label %if.end5

if.end5.thread:                                   ; preds = %ship.exit
  %2 = mul nuw nsw i32 %frame.089, 3
  %add = add nsw i32 %2, -15
  tail call fastcc void @disk(i32 noundef 241, i32 noundef %add, i32 noundef -9846) #3
  br label %if.end40

if.end5:                                          ; preds = %ship.exit
  %3 = add nsw i32 %frame.089, -10
  %or.cond41 = icmp ult i32 %3, 10
  br i1 %or.cond41, label %if.then9, label %if.end14

if.then9:                                         ; preds = %if.end5
  %4 = mul nuw nsw i32 %frame.089, 10
  %add13 = add nuw nsw i32 %4, 151
  tail call fastcc void @beam(i32 noundef %add13) #3
  br label %if.end40

if.end14:                                         ; preds = %if.end5
  %5 = add nsw i32 %frame.089, -20
  %or.cond42 = icmp ult i32 %5, 18
  br i1 %or.cond42, label %if.then18, label %if.end28

if.then18:                                        ; preds = %if.end14
  %cmp19 = icmp samesign ult i32 %frame.089, 28
  br i1 %cmp19, label %if.then20, label %if.end24

if.then20:                                        ; preds = %if.then18
  tail call fastcc void @beam(i32 noundef 350) #3
  %6 = mul nuw nsw i32 %frame.089, 5
  %add23 = add nsw i32 %6, -93
  tail call fastcc void @disk(i32 noundef 335, i32 noundef %add23, i32 noundef -8829) #3
  br label %if.end24

if.end24:                                         ; preds = %if.then20, %if.then18
  %7 = mul nuw nsw i32 %frame.089, 14
  %mul27 = add nsw i32 %7, -266
  tail call fastcc void @disk(i32 noundef 515, i32 noundef %mul27, i32 noundef -6544087) #3
  %div.i80.lhs.trunc = mul nuw nsw i32 %mul27, 3
  %div.i808186 = lshr i32 %div.i80.lhs.trunc, 2
  tail call fastcc void @disk(i32 noundef 515, i32 noundef %div.i808186, i32 noundef -1219802) #3
  %div1.i828387 = lshr exact i32 %mul27, 1
  tail call fastcc void @disk(i32 noundef 515, i32 noundef %div1.i828387, i32 noundef -18368) #3
  %div2.i848588 = lshr i32 %mul27, 2
  tail call fastcc void @disk(i32 noundef 515, i32 noundef %div2.i848588, i32 noundef -5206) #3
  br label %if.end40

if.end28:                                         ; preds = %if.end14
  %8 = add nsw i32 %frame.089, -38
  %or.cond43 = icmp ult i32 %8, 14
  br i1 %or.cond43, label %if.then32, label %if.end40

if.then32:                                        ; preds = %if.end28
  %cmp35 = icmp samesign ugt i32 %frame.089, 43
  %spec.store.select = select i1 %cmp35, i32 -15135465, i32 -12839136
  %.neg = mul nsw i32 %frame.089, -13
  %sub39 = add nsw i32 %.neg, 726
  tail call fastcc void @disk(i32 noundef 515, i32 noundef %sub39, i32 noundef %spec.store.select) #3
  br label %if.end40

if.end40:                                         ; preds = %if.then9, %if.end5.thread, %if.end24, %if.then32, %if.end28
  tail call void @simFlush() #4
  %inc = add nuw nsw i32 %frame.089, 1
  %exitcond.not = icmp eq i32 %inc, 56
  br i1 %exitcond.not, label %for.cond.cleanup, label %for.body, !llvm.loop !12
}

; Function Attrs: nounwind optsize sspstrong uwtable(sync)
define internal fastcc void @disk(i32 noundef range(i32 241, 516) %center_y, i32 noundef %radius, i32 noundef range(i32 -15135465, -5205) %color) unnamed_addr #0 {
entry:
  %sub = sub i32 %center_y, %radius
  %add = add i32 %radius, %center_y
  %cmp.not48 = icmp sgt i32 %sub, %add
  br i1 %cmp.not48, label %for.cond.cleanup, label %for.body.lr.ph

for.body.lr.ph:                                   ; preds = %entry
  %sub1 = sub i32 768, %radius
  %add3 = add i32 %radius, 768
  %cmp4.not46 = icmp sgt i32 %sub1, %add3
  %mul18 = mul i32 %radius, %radius
  br label %for.body

for.cond.cleanup:                                 ; preds = %for.cond.cleanup5, %entry
  ret void

for.body:                                         ; preds = %for.body.lr.ph, %for.cond.cleanup5
  %y.049 = phi i32 [ %sub, %for.body.lr.ph ], [ %inc21, %for.cond.cleanup5 ]
  br i1 %cmp4.not46, label %for.cond.cleanup5, label %for.body6.lr.ph

for.body6.lr.ph:                                  ; preds = %for.body
  %0 = icmp ult i32 %y.049, 768
  %sub8 = sub nsw i32 %y.049, %center_y
  %mul16 = mul i32 %sub8, %sub8
  br label %for.body6

for.cond.cleanup5:                                ; preds = %if.end, %for.body
  %inc21 = add i32 %y.049, 1
  %cmp.not = icmp sgt i32 %inc21, %add
  br i1 %cmp.not, label %for.cond.cleanup, label %for.body, !llvm.loop !13

for.body6:                                        ; preds = %for.body6.lr.ph, %if.end
  %x.047 = phi i32 [ %sub1, %for.body6.lr.ph ], [ %inc, %if.end ]
  %or.cond = icmp ult i32 %x.047, 1536
  %or.cond24 = and i1 %0, %or.cond
  br i1 %or.cond24, label %land.lhs.true15, label %if.end

land.lhs.true15:                                  ; preds = %for.body6
  %sub7 = add nsw i32 %x.047, -768
  %mul = mul nsw i32 %sub7, %sub7
  %add17 = add i32 %mul, %mul16
  %cmp19.not = icmp sgt i32 %add17, %mul18
  br i1 %cmp19.not, label %if.end, label %if.then

if.then:                                          ; preds = %land.lhs.true15
  tail call void @simPutPixel(i32 noundef %x.047, i32 noundef %y.049, i32 noundef %color) #4
  br label %if.end

if.end:                                           ; preds = %if.then, %land.lhs.true15, %for.body6
  %inc = add i32 %x.047, 1
  %cmp4.not = icmp sgt i32 %inc, %add3
  br i1 %cmp4.not, label %for.cond.cleanup5, label %for.body6, !llvm.loop !14
}

; Function Attrs: nounwind optsize sspstrong uwtable(sync)
define internal fastcc void @beam(i32 noundef %end_y) unnamed_addr #0 {
entry:
  %cmp.not26 = icmp slt i32 %end_y, 241
  br i1 %cmp.not26, label %for.cond.cleanup, label %for.cond1.preheader

for.cond1.preheader:                              ; preds = %entry, %for.cond.cleanup3
  %y.027 = phi i32 [ %inc13, %for.cond.cleanup3 ], [ 241, %entry ]
  br label %for.body4

for.cond.cleanup:                                 ; preds = %for.cond.cleanup3, %entry
  ret void

for.cond.cleanup3:                                ; preds = %for.body4
  %inc13 = add i32 %y.027, 1
  %cmp.not = icmp sgt i32 %inc13, %end_y
  br i1 %cmp.not, label %for.cond.cleanup, label %for.cond1.preheader, !llvm.loop !15

for.body4:                                        ; preds = %for.cond1.preheader, %for.body4
  %x.025 = phi i32 [ 755, %for.cond1.preheader ], [ %inc, %for.body4 ]
  %0 = add nsw i32 %x.025, -761
  %or.cond = icmp ult i32 %0, 15
  %spec.store.select = select i1 %or.cond, i32 -44186, i32 -9558914
  %1 = add nsw i32 %x.025, -766
  %or.cond15 = icmp ult i32 %1, 5
  %spec.store.select16 = select i1 %or.cond15, i32 -3651, i32 %spec.store.select
  tail call void @simPutPixel(i32 noundef %x.025, i32 noundef %y.027, i32 noundef %spec.store.select16) #4
  %inc = add nuw nsw i32 %x.025, 1
  %exitcond.not = icmp eq i32 %inc, 782
  br i1 %exitcond.not, label %for.cond.cleanup3, label %for.body4, !llvm.loop !16
}

; Function Attrs: optsize
declare void @simFlush() local_unnamed_addr #1

; Function Attrs: noinline nounwind optsize sspstrong uwtable(sync)
define internal fastcc void @box(i32 noundef %left, i32 noundef range(i32 -2147483648, 239) %top, i32 noundef %right, i32 noundef range(i32 -2147483647, 769) %bottom, i32 noundef range(i32 -16578798, -4021909) %color) unnamed_addr #2 {
entry:
  %cmp14 = icmp slt i32 %top, %bottom
  br i1 %cmp14, label %for.cond1.preheader.lr.ph, label %for.cond.cleanup

for.cond1.preheader.lr.ph:                        ; preds = %entry
  %cmp212 = icmp slt i32 %left, %right
  br label %for.cond1.preheader

for.cond1.preheader:                              ; preds = %for.cond1.preheader.lr.ph, %for.cond.cleanup3
  %y.015 = phi i32 [ %top, %for.cond1.preheader.lr.ph ], [ %inc6, %for.cond.cleanup3 ]
  br i1 %cmp212, label %for.body4, label %for.cond.cleanup3

for.cond.cleanup:                                 ; preds = %for.cond.cleanup3, %entry
  ret void

for.cond.cleanup3:                                ; preds = %for.body4, %for.cond1.preheader
  %inc6 = add i32 %y.015, 1
  %exitcond16.not = icmp eq i32 %inc6, %bottom
  br i1 %exitcond16.not, label %for.cond.cleanup, label %for.cond1.preheader, !llvm.loop !17

for.body4:                                        ; preds = %for.cond1.preheader, %for.body4
  %x.013 = phi i32 [ %inc, %for.body4 ], [ %left, %for.cond1.preheader ]
  tail call void @simPutPixel(i32 noundef %x.013, i32 noundef %y.015, i32 noundef %color) #4
  %inc = add i32 %x.013, 1
  %exitcond.not = icmp eq i32 %inc, %right
  br i1 %exitcond.not, label %for.cond.cleanup3, label %for.body4, !llvm.loop !18
}

; Function Attrs: optsize
declare void @simPutPixel(i32 noundef, i32 noundef, i32 noundef) local_unnamed_addr #1

attributes #0 = { nounwind optsize sspstrong uwtable(sync) "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="4" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+ccdp,+ccidx,+ccpp,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8a" "zero-call-used-regs"="used-gpr" }
attributes #1 = { optsize "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="4" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+ccdp,+ccidx,+ccpp,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8a" "zero-call-used-regs"="used-gpr" }
attributes #2 = { noinline nounwind optsize sspstrong uwtable(sync) "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="4" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+ccdp,+ccidx,+ccpp,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8a" "zero-call-used-regs"="used-gpr" }
attributes #3 = { optsize }
attributes #4 = { nounwind optsize }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 14, i32 4]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 8, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"clang version 21.1.8"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = distinct !{!8, !7}
!9 = distinct !{!9, !7}
!10 = distinct !{!10, !7}
!11 = distinct !{!11, !7}
!12 = distinct !{!12, !7}
!13 = distinct !{!13, !7}
!14 = distinct !{!14, !7}
!15 = distinct !{!15, !7}
!16 = distinct !{!16, !7}
!17 = distinct !{!17, !7}
!18 = distinct !{!18, !7}
