import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

with open('best_plant_disease_model_history.json') as f:
    h = json.load(f)

epochs = list(range(1, len(h['train_loss']) + 1))
best_val_acc = max(h['val_acc'])
best_epoch   = h['val_acc'].index(best_val_acc) + 1

fig = plt.figure(figsize=(14, 6), facecolor='#0f1117')
fig.suptitle('Plant Disease CNN  -  Training Results  (RTX 5050)',
             color='white', fontsize=15, fontweight='bold', y=1.01)

gs = gridspec.GridSpec(1, 2, wspace=0.35)

# Loss plot
ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor('#1a1d27')
ax1.plot(epochs, h['train_loss'], color='#4fc3f7', lw=2.5, marker='o', ms=5, label='Train Loss')
ax1.plot(epochs, h['val_loss'],   color='#f48fb1', lw=2.5, marker='s', ms=5, label='Val Loss')
ax1.axvline(best_epoch, color='#ffd54f', ls='--', lw=1.2, alpha=0.7, label='Best epoch (%d)' % best_epoch)
ax1.set_xlabel('Epoch', color='#ccc')
ax1.set_ylabel('Loss', color='#ccc')
ax1.set_title('Loss', color='white', fontsize=12)
ax1.legend(facecolor='#2a2d3a', labelcolor='white', edgecolor='#444')
ax1.tick_params(colors='#aaa')
for spine in ax1.spines.values():
    spine.set_edgecolor('#444')
ax1.grid(True, color='#2a2d3a', lw=0.8)

# Accuracy plot
ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor('#1a1d27')
ax2.plot(epochs, h['train_acc'], color='#80cbc4', lw=2.5, marker='o', ms=5, label='Train Acc')
ax2.plot(epochs, h['val_acc'],   color='#ce93d8', lw=2.5, marker='s', ms=5, label='Val Acc')
ax2.axvline(best_epoch, color='#ffd54f', ls='--', lw=1.2, alpha=0.7, label='Best epoch (%d)' % best_epoch)
ax2.axhline(best_val_acc, color='#a5d6a7', ls=':', lw=1.2, alpha=0.8, label='Best %.1f%%' % best_val_acc)
ax2.set_xlabel('Epoch', color='#ccc')
ax2.set_ylabel('Accuracy (%)', color='#ccc')
ax2.set_title('Accuracy', color='white', fontsize=12)
ax2.legend(facecolor='#2a2d3a', labelcolor='white', edgecolor='#444')
ax2.tick_params(colors='#aaa')
for spine in ax2.spines.values():
    spine.set_edgecolor('#444')
ax2.grid(True, color='#2a2d3a', lw=0.8)

# Stats annotation at bottom
stats = (
    'Best Val Acc : %.2f%%  (epoch %d)    '
    'Final Train : %.2f%%    '
    'Final Val : %.2f%%    '
    'Classes : 114'
) % (best_val_acc, best_epoch, h['train_acc'][-1], h['val_acc'][-1])

fig.text(0.5, -0.06, stats, ha='center', color='#aaaaaa', fontsize=10,
         bbox=dict(facecolor='#1a1d27', edgecolor='#444', boxstyle='round,pad=0.5'))

plt.tight_layout()
plt.savefig('training_history.png', dpi=150, bbox_inches='tight', facecolor='#0f1117')
print('Plot saved: training_history.png')
