# S07 terminal contact-shadow ownership fix

Base 4ada81efb509e3d29ede837a7f2d651f0eec93cb retains the independently restored original matchbox. This update additionally uses three human-only alpha masks for F100/103/106 contact projection, preserving original registration and contact parameters. The full original visible PNGs remain byte-identical and no longer cast the embedded physical lamp/table ellipse onto the floor.

Human alpha sources were assembled from the original pre-lamp body and complete hand layers by independent reviewer, not by clipping visible fingers. Production PNGs set RGB to black only; alpha is exactly identical and base row is1022. renderPaint contact calculation is independent of display alpha, so shadow-only layers use alpha:0 and original contact, followed by unchanged full visible layers. Shared helpers unchanged.

Only render100–107 at1920x1080/24fps, reuse exact f35f9ae2 first100 PNGs and encode full108. Decode099/100/102/103/105/106/107 to validate matchbox permanence, single carried lamp, stable foot shadow without false stretch, and lift. Ready/audio/EDL unchanged.
