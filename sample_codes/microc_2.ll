; ModuleID = 'microc_2.c'
source_filename = "microc_2.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
entry:
  %retval = alloca i32, align 4
  %a = alloca i32, align 4
  %b = alloca i32, align 4
  %c = alloca i32, align 4
  %d = alloca i32, align 4
  %e = alloca i32, align 4
  %f = alloca i32, align 4
  store i32 0, ptr %retval, align 4
  store i32 55, ptr %a, align 4
  store i32 5, ptr %b, align 4
  %0 = load i32, ptr %a, align 4
  %1 = load i32, ptr %b, align 4
  %mul = mul nsw i32 %0, %1
  store i32 %mul, ptr %c, align 4
  %2 = load i32, ptr %c, align 4
  %3 = load i32, ptr %b, align 4
  %add = add nsw i32 %2, %3
  store i32 %add, ptr %d, align 4
  %4 = load i32, ptr %a, align 4
  %5 = load i32, ptr %d, align 4
  %mul1 = mul nsw i32 %4, %5
  store i32 %mul1, ptr %f, align 4
  %6 = load i32, ptr %b, align 4
  ret i32 %6
}

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 18.1.3 (1ubuntu1)"}
