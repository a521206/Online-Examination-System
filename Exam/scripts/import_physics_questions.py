import os
import sys
import django

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
    django.setup()

setup_django()

from questions.question_models import Question_DB
from django.contrib.auth.models import User

# Get the first professor user
professor = User.objects.filter(groups__name='Professor').first()
if not professor:
    raise Exception('No professor user found!')

questions = [
    {
        'question': r"A uniform electric field pointing in positive X-direction exists in a region. Let A be the origin, B be the point on the X-axis at $x=+1$ cm and C be the point on the Y-axis at $y=+1$ cm. Then the potential at points A, B and C satisfy:",
        'optionA': r"$V_{A}<V_{B}$",
        'optionB': r"$V_{A}>V_{B}$",
        'optionC': r"$V_{A}<V_{C}$",
        'optionD': r"$V_{A}>V_{C}$",
        'answer': 'B',
        'max_marks': 1,
        'solution': r"In the direction of electric field, the electric potential decreases. Since the field points in positive X-direction, potential decreases as we move along positive X-axis. Therefore, $V_{A}>V_{B}$."
    },
    {
        'question': r"A conducting wire connects two charged conducting spheres of radii $r_{1}$ and $r_{2}$ such that they attain equilibrium with respect to each other. The distance of separation between the two spheres is very large as compared to either of their radii. The ratio of the magnitudes of the electric fields at the surfaces of the spheres of radii $r_{1}$ and $r_{2}$ is:",
        'optionA': r"$\frac{r_{1}}{r_{2}}$",
        'optionB': r"$\frac{r_{2}}{r_{1}}$",
        'optionC': r"$\frac{r_{2}^{2}}{r_{1}^{2}}$",
        'optionD': r"$\frac{r_{1}^{2}}{r_{2}^{2}}$",
        'answer': 'B',
        'max_marks': 1,
        'solution': r"In the state of equilibrium, the potential on the surface of both spheres is equal. $\frac{kq_{1}}{r_{1}}=\frac{kq_{2}}{r_{2}}\Rightarrow\frac{q_{1}}{q_{2}}=\frac{r_{1}}{r_{2}}$. Electric field at surface $E=\frac{kq}{r^{2}}$. $\frac{E_{1}}{E_{2}}=\frac{q_{1}}{q_{2}}\frac{r_{2}^{2}}{r_{1}^{2}}=\frac{r_{1}}{r_{2}}\cdot\frac{r_{2}^{2}}{r_{1}^{2}}=\frac{r_{2}}{r_{1}}$."
    },
    {
        'question': r"A long straight wire of circular cross section of radius 'a' carries a steady current I. The current is uniformly distributed across its cross section. The ratio of magnitudes of the magnetic field at a point $\frac{a}{2}$ above the surface of wire to that of a point $\frac{a}{2}$ below its surface is:",
        'optionA': '4:1',
        'optionB': '1:1',
        'optionC': '4:3',
        'optionD': '3:4',
        'answer': 'C',
        'max_marks': 1,
        'solution': r"At P2 (above surface), $B_{2}=\frac{\mu_{0}I}{2\pi(\frac{3a}{2})}=\frac{\mu_{0}I}{3\pi a}$. At P1 (below surface), $B_{1}=\frac{\mu_{0}(I/4)}{2\pi(a/2)}=\frac{\mu_{0}I}{4\pi a}$. $\frac{B_{2}}{B_{1}}=\frac{(\frac{\mu_{0}I}{3\pi a})}{(\frac{\mu_{0}I}{4\pi a})}=\frac{4}{3}$."
    },
    {
        'question': r"The diffraction effect can be observed in:",
        'optionA': 'sound waves only',
        'optionB': 'light waves only',
        'optionC': 'ultrasonic waves only',
        'optionD': 'sound waves as well as light waves',
        'answer': 'D',
        'max_marks': 1,
        'solution': r"Diffraction is a wave phenomenon that occurs when waves encounter obstacles or pass through apertures. It can be observed in all types of waves including sound waves, light waves, and ultrasonic waves."
    },
    {
        'question': r"A capacitor consists of two parallel plates, with an area of cross-section of 0.001 $m^{2}$, separated by a distance of 0.0001 m. If the voltage across the plates varies at the rate of $10^{8}$ V/s, then the value of displacement current through the capacitor is:",
        'optionA': r"$8.85\times10^{-3}$ A",
        'optionB': r"$8.85\times10^{-4}$ A",
        'optionC': r"$7.85\times10^{-3}$ A",
        'optionD': r"$9.85\times10^{-3}$ A",
        'answer': 'A',
        'max_marks': 1,
        'solution': r"Displacement current $I_{d}=\epsilon_{0}\frac{d\phi_{E}}{dt}=\epsilon_{0}A\frac{dE}{dt}=\epsilon_{0}A\frac{d}{dt}(\frac{V}{d})=\epsilon_{0}\frac{A}{d}\frac{dV}{dt}=8.85\times10^{-12}\times\frac{0.001}{0.0001}\times10^{8}=8.85\times10^{-3}$ A."
    },
    {
        'question': r"In a series LCR circuit, the voltage across the resistance, capacitance and inductance is 10 V each. If the capacitance is short circuited, the voltage across the inductance will be:",
        'optionA': '10 V',
        'optionB': r"$10\sqrt{2}$ V",
        'optionC': r"$\frac{10}{\sqrt{2}}$ V",
        'optionD': '20 V',
        'answer': 'C',
        'max_marks': 1,
        'solution': r"$IR=IX_{C}=IX_{L}=10$ V. $X_{C}=X_{L}=R$. $Z=\sqrt{R^{2}+(X_{C}-X_{L})^{2}}=\sqrt{R^{2}+(R-R)^{2}}=R$. $V_{S}=IZ=IR=10$ V. When the capacitor is short circuited then $Z=\sqrt{R^{2}+X_{L}^{2}}=\sqrt{R^{2}+R^{2}}=R\sqrt{2}$. $V_{L}=I'X_{L}=\frac{10}{\sqrt{2}R}\times R=\frac{10}{\sqrt{2}}$ V."
    },
    {
        'question': r"Correct match of column I with column II is:",
        'optionA': '1-P, 2-R, 3-S, 4-Q',
        'optionB': '1-S, 2-P, 3-Q, 4-R',
        'optionC': '1-Q, 2-P, 3-S, 4-R',
        'optionD': '1-S, 2-R, 3-P, 4-Q',
        'answer': 'B',
        'max_marks': 1,
        'solution': r"The correct matching is: 1-S, 2-P, 3-Q, 4-R. This is based on the physical properties and relationships between the quantities listed in the columns."
    },
    {
        'question': r"The distance of closest approach of an alpha particle is d when it moves with a speed V towards a nucleus. Another alpha particle is projected with higher energy such that the new distance of the closest approach is $\frac{d}{2}$. What is the speed of projection of the alpha particle in this case?",
        'optionA': r"$\frac{V}{2}$",
        'optionB': r"$\sqrt{2}V$",
        'optionC': '2V',
        'optionD': '4V',
        'answer': 'B',
        'max_marks': 1,
        'solution': r"$d=\frac{const}{V_{1}^{2}}$ ...(1). $\frac{d}{2}=\frac{const}{V_{2}^{2}}$ ...(2). From equations (1) and (2), $2=\frac{V_{2}^{2}}{V_{1}^{2}}\Rightarrow V_{2}=\sqrt{2}V_{1}$. Given, $(V_{1}=V)$ so $V_{2}=\sqrt{2}V$."
    },
    {
        'question': r"A point object is placed at the centre of a glass sphere of radius 6 cm and refractive index 1.5. The distance of virtual image from the surface of the sphere is:",
        'optionA': '2 cm',
        'optionB': '4 cm',
        'optionC': '6 cm',
        'optionD': '12 cm',
        'answer': 'C',
        'max_marks': 1,
        'solution': r"$n_{2}=1$, $n_{1}=1.5$, $u=6$ cm, $R=6$ cm. $\frac{n_{2}}{v}-\frac{n_{1}}{u}=\frac{n_{2}-n_{1}}{R}$. $\frac{1}{v}-\frac{1.5}{-6}=\frac{1-1.5}{-6}$. $\frac{1}{v}=\frac{-1.5}{6}+\frac{0.5}{6}=\frac{-1}{6}$. $v=-6$ cm."
    },
    {
        'question': r"Colours observed on a CD (Compact Disk) is due to:",
        'optionA': 'Reflection',
        'optionB': 'Diffraction',
        'optionC': 'Dispersion',
        'optionD': 'Absorption',
        'answer': 'B',
        'max_marks': 1,
        'solution': r"The colors observed on a CD are due to diffraction. The closely spaced grooves on the CD surface act as a diffraction grating, causing light to diffract and produce the colorful patterns."
    },
    {
        'question': r"The number of electrons made available for conduction by dopant atoms depends strongly upon:",
        'optionA': 'doping level',
        'optionB': 'increase in ambient temperature',
        'optionC': 'energy gap',
        'optionD': 'options (A) and (B) both',
        'answer': 'A',
        'max_marks': 1,
        'solution': r"The number of electrons made available for conduction by dopant atoms depends primarily on the doping level, which determines how many impurity atoms are present in the semiconductor."
    },
    {
        'question': r"If copper wire is stretched to make its radius decrease by 0.1%, then the percentage change in its resistance is approximately:",
        'optionA': '-0.4%',
        'optionB': '+0.8%',
        'optionC': '+0.4%',
        'optionD': '+0.2%',
        'answer': 'C',
        'max_marks': 1,
        'solution': r"Resistance $R=\rho\frac{l}{A}=\rho\frac{l}{\pi r^{2}}$. When radius decreases by 0.1%, $r'=0.999r$. $R'=\rho\frac{l}{\pi(0.999r)^{2}}=\rho\frac{l}{\pi r^{2}}\times\frac{1}{(0.999)^{2}}\approx R\times1.002$. Percentage change = +0.4%."
    },
]

for q in questions:
    obj, created = Question_DB.objects.get_or_create(
        question=q['question'],
        optionA=q['optionA'],
        optionB=q['optionB'],
        optionC=q['optionC'],
        optionD=q['optionD'],
        answer=q['answer'],
        max_marks=q['max_marks'],
        solution=q['solution'],
        professor=professor
    )
    print(f"{'Created' if created else 'Exists'}: {q['question'][:60]}...")
print("Import complete.") 