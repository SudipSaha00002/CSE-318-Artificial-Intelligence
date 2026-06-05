import matplotlib.pyplot as plt
import numpy as np

graphs = ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9', 'g10','g11']
# graphs = ['g12', 'g13', 'g14', 'g15', 'g16', 'g17', 'g18', 'g19', 'g20','g21','g22']
# graphs = ['g23', 'g24', 'g25', 'g26', 'g27', 'g28', 'g29', 'g30','g31', 'g32', 'g33']
# graphs = ['g34', 'g35', 'g36', 'g37', 'g38', 'g39', 'g40','g41', 'g42', 'g43', 'g44']
# graphs = ['g45', 'g46', 'g47', 'g48', 'g49', 'g50','g51', 'g52', 'g53', 'g54']

randomized = [9560, 9586, 9582, 9592, 9569, 86, -73, -73, -23, -61, 24] 
# randomized = [1, 25, 2339, 2329, 2350, 2337, 7, -59, -24,-30, 9982] 
# randomized = [ 9999, 10019, 10035, 10007, -18, -54, 9, 79, -31, 8, -25] 
# randomized = [-20, 5891, 5873, 5891, 5902, 0, -54, 7, 83, 4997, 4986] 
# randomized = [ 4975, 4984, 5000, 3016, 3019, 3005,2962, 2945, 2938, 2948] 


greedy = [11346, 11204, 11254, 11229, 11277, 1742, 1573, 1586, 1701, 1556, 484]
# greedy = [480, 498, 2917, 2883, 2895, 2925, 846, 756, 813,764, 12773]
# greedy = [12827, 12780, 12752, 12852, 2694, 2682, 2739, 2778,2699, 1226, 1210]
# greedy = [ 1210, 7264, 7294, 7296, 7298, 2026, 2009, 2058, 2115, 6390, 6428]
# greedy = [ 6366, 6362, 6437, 6000, 6000, 5880, 3661, 3653, 3660, 3656]


semi_greedy = [11141, 11143, 11150, 11149, 11147, 1600, 1433, 1434, 1479, 1434, 423]
# semi_greedy = [407, 429, 2939, 2918, 2921, 2921, 729, 649, 686, 665, 12656]
# semi_greedy = [12675, 12675, 12666, 12663, 2404, 2376, 2454, 2471, 2372, 1044, 1013]
# semi_greedy = [1010, 7366, 7356, 7366, 7362, 1707, 1729, 1735, 1807, 6315, 6315]
# semi_greedy = [6302, 6310, 6320, 6000, 6000, 5858, 3690, 3690, 3686, 3689]


local_search = [11371, 11372, 11359, 11385, 11372, 1907, 1729, 1733, 1776, 1726, 450]
# local_search = [436, 461, 2969, 2948, 2953, 2951, 837, 761, 780, 775, 12890]
# local_search = [12913, 12907, 12903, 12894, 2813, 2780, 2878, 2874, 2798, 1112, 1088]
# local_search = [1087, 7442, 7433, 7442, 7441, 2009, 2008, 2010, 2086, 6437, 6441]
# local_search = [6430, 6433, 6437, 6000, 6000, 5859, 3731, 3730, 3727, 3727]


grasp = [11445, 11463, 11440, 11477, 11474, 1978, 1827, 1830, 1843, 1811, 472]
# grasp = [466, 490, 2990, 2968, 2979, 2981, 884, 825, 823, 821, 12977]
# grasp = [13002, 13001, 12989, 12970, 2932, 2874, 2981, 2955, 2904, 1154, 1134]
# grasp = [1146, 7474, 7491, 7474, 7463, 2074, 2068, 2124, 2158, 6524, 6499]
# grasp = [6480, 6509, 6496, 6000, 6000, 5874, 3753, 3751, 3757, 3748]


barWidth = 0.15
fig, ax = plt.subplots(figsize=(14, 8))

br1 = np.arange(len(graphs))
br2 = [x + barWidth for x in br1]
br3 = [x + barWidth for x in br2]
br4 = [x + barWidth for x in br3]
br5 = [x + barWidth for x in br4]

ax.bar(br1, randomized, width=barWidth, label='Randomized', color='blue')
ax.bar(br2, greedy, width=barWidth, label='Greedy', color='red')
ax.bar(br3, semi_greedy, width=barWidth, label='Semi-Greedy', color='purple')
ax.bar(br5, grasp, width=barWidth, label='GRASP', color='cyan')
ax.bar(br4, local_search, width=barWidth, label='Local Search', color='yellow')


ax.yaxis.grid(True, linestyle='--', alpha=0.7, color='white')
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)


ax.set_facecolor('#333333')
fig.patch.set_facecolor('#333333')

ax.set_ylim(-2000, 15000)


ax.set_xlabel('', fontsize=12)
ax.set_title('Max Cut (Graph 1-10)', color='white', fontsize=16, pad=20)
ax.set_xticks([r + barWidth*2 for r in range(len(graphs))])
ax.set_xticklabels(graphs, color='white')
ax.tick_params(axis='y', colors='white')


yticks = [-2000, 0, 2000, 4000, 6000, 8000, 10000, 12000]
ax.set_yticks(yticks)
ax.set_yticklabels([str(y) for y in yticks], color='white')


ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5, frameon=False, 
          facecolor='#333333', labelcolor='white')


plt.tight_layout()


plt.show()