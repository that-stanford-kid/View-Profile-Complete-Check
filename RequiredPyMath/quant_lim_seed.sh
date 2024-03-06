~/$ awk 'BEGIN{for(i=1;i<=10;i++) {for(j=1;j<=14;j+=5) {print "Simulation " i " Interval " j; for(k=j;k<j+5;k++) {printf "Price for interval %d: %d, ", k, 100+int(rand()*50)}; print ""}}}'
or | and
~/$ awk 'BEGIN {
>     srand(); # Seed the random number generator
>     for (i = 1; i <= 10; i++) {
>         for (j = 1; j <= 14; j += 5) {
>             print "Simulation", i, "Interval", j;
>             for (k = j; k < j + 5; k++) {
>                 printf "Price for interval %d: %d, ", k, 100 + int(rand() * 50);
>             }
>             print "";
>         }
>     }
> }'

```
output_table:
  Simulation 1 Interval 1
  Price for interval 1: 118, Price for interval 2: 133, Price for interval 3: 135, Price for interval 4: 135, Price for interval 5: 139, 
  Simulation 1 Interval 6
  Price for interval 6: 126, Price for interval 7: 147, Price for interval 8: 126, Price for interval 9: 116, Price for interval 10: 130, 
  Simulation 1 Interval 11
  Price for interval 11: 107, Price for interval 12: 124, Price for interval 13: 120, Price for interval 14: 141, Price for interval 15: 104, 
  Simulation 2 Interval 1
  Price for interval 1: 135, Price for interval 2: 120, Price for interval 3: 141, Price for interval 4: 126, Price for interval 5: 120, 
  Simulation 2 Interval 6
  Price for interval 6: 143, Price for interval 7: 112, Price for interval 8: 139, Price for interval 9: 127, Price for interval 10: 109, 
  Simulation 2 Interval 11
  Price for interval 11: 136, Price for interval 12: 100, Price for interval 13: 105, Price for interval 14: 127, Price for interval 15: 120, 
  Simulation 3 Interval 1
  Price for interval 1: 123, Price for interval 2: 146, Price for interval 3: 104, Price for interval 4: 109, Price for interval 5: 132, 
  Simulation 3 Interval 6
  Price for interval 6: 143, Price for interval 7: 135, Price for interval 8: 130, Price for interval 9: 119, Price for interval 10: 102, 
  Simulation 3 Interval 11
  Price for interval 11: 110, Price for interval 12: 127, Price for interval 13: 126, Price for interval 14: 131, Price for interval 15: 118, 
  Simulation 4 Interval 1
  Price for interval 1: 130, Price for interval 2: 116, Price for interval 3: 139, Price for interval 4: 122, Price for interval 5: 143, 
  Simulation 4 Interval 6
  Price for interval 6: 110, Price for interval 7: 115, Price for interval 8: 106, Price for interval 9: 149, Price for interval 10: 142, 
  Simulation 4 Interval 11
  Price for interval 11: 116, Price for interval 12: 136, Price for interval 13: 142, Price for interval 14: 121, Price for interval 15: 113, 
  Simulation 5 Interval 1
  Price for interval 1: 113, Price for interval 2: 145, Price for interval 3: 110, Price for interval 4: 117, Price for interval 5: 104, 
  Simulation 5 Interval 6
  Price for interval 6: 143, Price for interval 7: 110, Price for interval 8: 140, Price for interval 9: 123, Price for interval 10: 129, 
  Simulation 5 Interval 11
  Price for interval 11: 142, Price for interval 12: 134, Price for interval 13: 106, Price for interval 14: 118, Price for interval 15: 115, 
  Simulation 6 Interval 1
  Price for interval 1: 125, Price for interval 2: 148, Price for interval 3: 132, Price for interval 4: 114, Price for interval 5: 121, 
  Simulation 6 Interval 6
  Price for interval 6: 126, Price for interval 7: 124, Price for interval 8: 136, Price for interval 9: 132, Price for interval 10: 124, 
  Simulation 6 Interval 11
  Price for interval 11: 129, Price for interval 12: 148, Price for interval 13: 110, Price for interval 14: 122, Price for interval 15: 120, 
  Simulation 7 Interval 1
  Price for interval 1: 124, Price for interval 2: 135, Price for interval 3: 116, Price for interval 4: 135, Price for interval 5: 102, 
  Simulation 7 Interval 6
  Price for interval 6: 121, Price for interval 7: 128, Price for interval 8: 113, Price for interval 9: 111, Price for interval 10: 101, 
  Simulation 7 Interval 11
  Price for interval 11: 142, Price for interval 12: 103, Price for interval 13: 135, Price for interval 14: 149, Price for interval 15: 122, 
  Simulation 8 Interval 1
  Price for interval 1: 101, Price for interval 2: 124, Price for interval 3: 121, Price for interval 4: 133, Price for interval 5: 139, 
  Simulation 8 Interval 6
  Price for interval 6: 142, Price for interval 7: 110, Price for interval 8: 113, Price for interval 9: 129, Price for interval 10: 143, 
  Simulation 8 Interval 11
  Price for interval 11: 138, Price for interval 12: 108, Price for interval 13: 142, Price for interval 14: 148, Price for interval 15: 130, 
  Simulation 9 Interval 1
  Price for interval 1: 112, Price for interval 2: 123, Price for interval 3: 116, Price for interval 4: 129, Price for interval 5: 108, 
  Simulation 9 Interval 6
  Price for interval 6: 118, Price for interval 7: 100, Price for interval 8: 136, Price for interval 9: 131, Price for interval 10: 112, 
  Simulation 9 Interval 11
  Price for interval 11: 137, Price for interval 12: 124, Price for interval 13: 116, Price for interval 14: 123, Price for interval 15: 124, 
  Simulation 10 Interval 1
  Price for interval 1: 138, Price for interval 2: 125, Price for interval 3: 149, Price for interval 4: 110, Price for interval 5: 109, 
  Simulation 10 Interval 6
  Price for interval 6: 138, Price for interval 7: 102, Price for interval 8: 119, Price for interval 9: 102, Price for interval 10: 132, 
  Simulation 10 Interval 11
  Price for interval 11: 112, Price for interval 12: 140, Price for interval 13: 140, Price for interval 14: 104, Price for interval 15: 13 """
  }}"
