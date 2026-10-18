"""Manual Bezier construction for the two authorized S22 contact references. No image generation."""
from pathlib import Path
P=Path(__file__).resolve().parent
# The curved outlines below are individually authored; not traced old h22 or code-card poses.
def path(d,fill='url(#cskin)',stroke='#684635',width=3.5):return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'
def crease(d,colour='#b97755',width=2.2):return path(d,'none',colour,width)
def ellipse(cx,cy,rx,ry,fill,stroke='#a56e50',rot=0):return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="1.8" transform="rotate({rot} {cx} {cy})"/>'
DEFS='''<defs>
 <linearGradient id="cskin" x1="0" y1="0" x2=".25" y2="1"><stop offset="0" stop-color="#f6cba7"/><stop offset=".58" stop-color="#f0bc94"/><stop offset="1" stop-color="#dca17a"/></linearGradient>
 <linearGradient id="gskin" x1="0" y1="0" x2=".15" y2="1"><stop offset="0" stop-color="#e8bd95"/><stop offset=".6" stop-color="#dbab82"/><stop offset="1" stop-color="#c68c68"/></linearGradient>
 <linearGradient id="rod" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d5ab61"/><stop offset="1" stop-color="#9e7437"/></linearGradient>
</defs>'''
CBEGIN='<g transform="translate(700 700) rotate(-24.285)">';G0='<g transform="translate(-90 -70) rotate(-6 650 500)">'
# Wrist and palm form one uninterrupted outline, with four distinct curled finger volumes.
CBASE=path('M -950 -84 C -640 -98 -265 -68 -44 -55 C -8 -57 22 -73 58 -75 C 106 -79 139 -69 158 -47 C 179 -27 183 0 174 30 C 162 54 128 75 86 78 C 42 77 15 64 -29 56 C -270 64 -650 91 -950 104 Z')
CFINGERS=''.join([
path('M 128 -44 C 142 -71 170 -81 199 -76 C 227 -72 250 -54 265 -31 C 278 -11 273 7 258 15 C 246 21 230 10 227 -3 C 221 -23 204 -33 181 -30 L 158 -12 Z'),
path('M 143 -7 C 168 -25 196 -19 219 -2 C 244 16 260 31 250 47 C 241 61 225 57 211 47 L 184 29 L 160 32 Z'),
path('M 137 24 C 159 9 189 17 209 36 C 229 53 233 73 219 85 C 206 95 188 85 178 74 L 152 56 Z'),
path('M 111 48 C 132 34 153 39 171 54 C 191 72 195 90 180 101 C 167 110 150 102 137 88 L 114 77 Z')])
CNAILS=''.join([ellipse(258,-2,7,13,'#f6d9bd',rot=-22),ellipse(239,40,10,7,'#f6d9bd',rot=28),ellipse(210,75,10,7,'#f6d9bd',rot=35),ellipse(174,91,9,6,'#f6d9bd',rot=40)])
CCREASE=''.join([crease('M -27 -45 Q -7 -35 3 -30'),crease('M -20 43 Q -2 33 9 31'),crease('M 52 28 C 77 43 103 40 124 31'),crease('M 176 -53 Q 196 -48 208 -35'),crease('M 185 9 Q 200 16 207 28'),crease('M 163 42 Q 179 51 186 65'),crease('M 143 66 Q 158 76 164 87')])
CTHUMB=path('M 43 -26 C 64 -46 88 -57 112 -55 C 144 -56 164 -34 184 -23 L 226 -14 C 244 -8 256 5 250 21 C 244 38 227 43 211 31 L 165 9 C 135 -1 117 -9 93 -4 C 69 1 53 -3 43 -26 Z')+ellipse(231,13,14,8,'#f9dcc3',rot=28)+crease('M 160 -22 Q 172 -12 175 0')+crease('M 93 -34 Q 116 -39 131 -28')
CHILD_FAR=CBEGIN+CBASE+CFINGERS+CNAILS+CCREASE+'</g>'
CHILD_NEAR=CBEGIN+CTHUMB+'</g>'
ROD='<g transform="translate(926 598) rotate(-30)"><rect x="0" y="-8" width="1200" height="16" rx="2" fill="url(#rod)" stroke="#79502e" stroke-width="2.4"/>'+crease('M 0 -3 L 1200 -3','#e9c77f',3)+'</g>'
# Adult far forearm/palm. The bare wrist has no jade: chosen hand is RIGHT.
GARM=path('M -120 250 C 140 298 407 385 624 443 C 656 433 692 441 721 458 C 758 475 797 503 830 540 C 850 559 859 588 850 610 C 841 633 819 641 795 630 C 763 621 741 603 717 587 C 683 568 654 553 627 550 C 395 503 127 456 -120 425 Z','url(#gskin)')
GWRINKLES=''.join([crease('M 626 458 Q 640 476 640 493','#a77356'),crease('M 620 472 Q 632 489 631 506','#ad7b5d'),crease('M 679 482 C 711 491 733 508 748 526','#b7815e'),crease('M 704 477 Q 720 481 729 489','#b7815e')])
# Four finger routes, mostly hidden by the child's volume after closure.
GCURL=''.join([
path('M 815 535 C 846 544 877 571 883 601 L 883 657 C 888 683 879 705 865 720 C 853 732 838 724 838 709 L 842 665 C 837 632 819 603 799 584 Z','url(#gskin)'),
path('M 799 555 C 829 577 842 612 846 646 L 846 698 C 848 722 843 743 834 750 C 819 759 807 746 809 731 L 814 686 C 816 646 803 610 782 588 Z','url(#gskin)'),
path('M 779 574 C 808 598 819 635 821 669 L 823 716 C 822 741 815 757 803 758 C 791 760 781 746 785 733 L 790 691 C 790 650 779 619 762 600 Z','url(#gskin)'),
path('M 760 585 C 783 610 796 644 799 679 L 799 713 C 800 735 792 748 780 747 C 768 746 762 735 766 721 L 769 690 C 769 654 758 629 743 609 Z','url(#gskin)')])
# Adult near thumb rests on child's proximal dorsum, >90px behind rod contact.
GTHUMB=path('M 704 509 C 726 501 750 511 770 533 L 814 579 C 832 589 841 605 832 620 C 823 636 802 634 786 621 L 747 590 C 726 579 710 572 694 556 C 683 543 689 520 704 509 Z','url(#gskin)')+ellipse(816,607,14,9,'#e8c9ae',rot=35)+crease('M 766 563 Q 776 574 778 585','#a77555')+crease('M 741 539 Q 750 544 755 554','#a77555')
# Visible caps join the hidden curling paths at the ulnar edge. Four, no extra digit.
GCAPS=''.join([path('M 853 707 C 860 705 869 709 875 717 C 880 729 874 739 865 740 C 854 741 847 730 848 720 Z','url(#gskin)')+ellipse(864,727,8,5,'#e7c7ac',rot=27),path('M 823 728 C 832 723 843 729 847 739 C 849 752 840 759 831 756 C 822 754 817 739 823 728 Z','url(#gskin)')+ellipse(834,746,8,5,'#e7c7ac',rot=25),path('M 794 735 C 804 729 814 735 817 745 C 819 758 809 764 800 759 C 790 755 788 743 794 735 Z','url(#gskin)')+ellipse(804,750,8,5,'#e7c7ac',rot=20),path('M 769 725 C 778 720 788 726 792 735 C 795 747 785 754 777 750 C 768 748 765 736 769 725 Z','url(#gskin)')+ellipse(780,740,7,5,'#e7c7ac',rot=20)])
# In F000 the adult fingers are open and lifted: actual contours stay separate from child.
GOPEN=''.join([
path('M 815 535 C 840 526 861 538 887 546 L 943 557 C 959 562 961 577 950 584 C 940 592 924 586 913 582 L 858 572 L 819 568 Z','url(#gskin)'),
path('M 802 554 C 827 546 854 559 880 572 L 930 589 C 947 596 943 612 930 615 C 919 617 906 611 894 607 L 846 594 L 806 589 Z','url(#gskin)'),
path('M 786 575 C 809 567 834 579 858 594 L 902 611 C 916 618 912 634 898 635 C 888 636 877 630 867 625 L 824 611 L 789 609 Z','url(#gskin)'),
path('M 765 589 C 785 584 807 596 824 609 L 859 625 C 874 633 871 647 859 649 C 849 651 836 644 828 639 L 793 625 L 766 622 Z','url(#gskin)')])
# Open hand fingertips after translation end at ~869,514; positive separation from child.
GOPEN=GOPEN.replace('url(#gskin)','url(#gskin)')
# The open-finger authorship uses y down before the -90/-70 hover transform.
def svg(parts,bg=True):return '<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">'+DEFS+('<rect width="1920" height="1080" fill="#faf8f1"/>' if bg else '')+''.join(parts)+'</svg>'
for frame in [0,24]:
 if frame==0:
  adult=G0+GARM+GOPEN+GWRINKLES+GTHUMB+'</g>'
  # open anatomy is all visible; no adult curl caps in hover state.
  parts=[adult,CHILD_FAR,ROD,CHILD_NEAR]
 else:
  adultfar=GARM+GCURL+GWRINKLES
  adultnear=GTHUMB+GCAPS
  adult=adultfar+adultnear;parts=[adultfar,CHILD_FAR,ROD,CHILD_NEAR,adultnear]
 (P/f'F{frame:03d}_volume_source.svg').write_text(svg(parts))
 # Internal transparent masks for local QA only; rendered to /tmp, not extra requested references.
 Path(f'/tmp/s22_G{frame:03d}.svg').write_text(svg([adult],False))
 Path(f'/tmp/s22_C{frame:03d}.svg').write_text(svg([CHILD_FAR,CHILD_NEAR],False))
print('Two manually authored volume contour SVGs written; exposure table untouched; image calls0.')
