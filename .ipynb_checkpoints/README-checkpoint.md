# Simple Bike Simulation

Based on a question in StackExchange Physics:

Question by [Ocharies](https://physics.stackexchange.com/users/102586/ocharles):
 [How can I model the acceleration/velocity of a bicycle knowing only the power output from the drivetrain and rider weight](https://physics.stackexchange.com/q/226854)

[Accepted answer](https://physics.stackexchange.com/a/226892) by [Floris](https://physics.stackexchange.com/users/26969/floris).


# Areo

I estimated the frontalArea from a flat section of a [ride](https://veloviewer.com/athletes/2039/activities/2802129759)
I did between time 00:15:47 - 00:17:32. Then in the "Power (meter)" graph for that section I produced
an avgerage Power of 142W at an average speed of 17.00mph.  I then twiddled the the frontalArea variable
until max speed calculated was 17.00mph.

[Here](https://www.triradar.com/training-advice/how-to-calculate-your-drag/) is another method for
estimating the forntalArea using photoshop. When I do that I iwll then adjust the dragCoeff variable
until the speed is again calculated to be 17.00mph.
