Name = "Directional Cycle Tool"
Version = "1.1"
DevVersion = False

FeetNumber = 2
Bake = True

if DevVersion:
    Version = f"{Version} (Dev)"
    FeetNumber = 4
    Bake = False

Title = f"{Name} - {Version}"
