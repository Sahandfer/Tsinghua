import torch.nn.functional as F
from tqdm import tqdm, trange


def validate(model, val_iterator, criterion, use_improved=True):
    val_loss = 0.0
    num_correct, num_total = 0, 0

    model.eval()
    for batch in val_iterator:
        if use_improved:
            output, y = model(batch)
        else:
            x, l = batch.sentence
            y = batch.label
            output = model(x, l)

        loss = criterion(output, y)
        val_loss += loss.item()

        preds = output.argmax(dim=1)
        num_correct += (preds == y).sum()
        num_total += preds.size()[0]

    val_loss = val_loss / len(val_iterator)
    acc = num_correct * 100 / num_total
    print(f"\n Validation Loss: {val_loss} | Accuracy: {acc}%\n")

    return val_loss


def train(
    model,
    train_iterator,
    val_iterator,
    optimizer,
    criterion,
    max_epoch,
    use_improved=True,
):
    best_model = None
    best_loss = 10
    prev_loss = 0
    overfit_num = 0
    for e in trange(max_epoch):
        train_loss = 0.0
        num_correct, num_total = 0, 0

        model.train()
        for batch in tqdm(train_iterator):
            if use_improved:
                output, y = model(batch)
            else:
                x, l = batch.sentence
                y = batch.label
                output = model(x, l)

            optimizer.zero_grad()
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()

            preds = output.argmax(dim=1)
            num_correct += (preds == y).sum()
            num_total += preds.size()[0]

            train_loss += loss.item()

        train_loss = train_loss / len(train_iterator)
        acc = num_correct * 100 / num_total

        print(f"\n Epoch {e+1} --> Training Loss: {train_loss} | Accuracy: {acc}%\n")

        val_loss = validate(model, val_iterator, criterion, use_improved)

        if val_loss > prev_loss and prev_loss != 0:
            prev_loss = val_loss
            overfit_num += 1
        else:
            overfit_num = 0

        if overfit_num >= 2:
            print("Early stoppage due to overfitting")
            break

        if val_loss < best_loss:
            best_loss = val_loss
            best_model = model

    return best_model
