import torch
import argparse
import numpy as np
import torch.optim as optim
from tqdm.auto import tqdm, trange
from transformers import AdamW, get_linear_schedule_with_warmup
from torch.utils.data import DataLoader, RandomSampler
from src.dataset import WikipediaCorpus
from torch.nn import DataParallel
from torch.utils.data import random_split
from src.model import Word2Vec


class Args:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser()

        parser.add_argument("--do_train", default=False, action="store_true")
        parser.add_argument("--do_eval", default=False, action="store_true")
        parser.add_argument("--do_test", default=False, action="store_true")
        parser.add_argument("--use_cuda", default=False, action="store_true")
        parser.add_argument("--dataset", default="wiki_t.txt", type=str)
        parser.add_argument("--output_dir", default="output", type=str)
        parser.add_argument("--cache_dir", default="cached", type=str)
        parser.add_argument("--batch_size", default=1, type=int)
        parser.add_argument("--window_size", default=2, type=int)
        parser.add_argument("--neg_sample_size", default=5, type=int)
        parser.add_argument("--embedding_size", default=100, type=int)
        parser.add_argument("--n_gpu", default=torch.cuda.device_count(), type=int)
        parser.add_argument("--learning_rate", default=5e-5, type=float)
        parser.add_argument("--weight_decay", default=0.0, type=float)
        parser.add_argument("--adam_epsilon", default=1e-8, type=float)
        parser.add_argument("--max_grad_norm", default=1.0, type=float)
        parser.add_argument("--max_steps", default=-1, type=int)
        parser.add_argument("--warmup_steps", default=0, type=int)
        parser.add_argument("--log_loss", default=10000, type=int)
        parser.add_argument("--num_train_epochs", default=1, type=int)
        parser.add_argument("--gradient_accumulation_steps", default=1, type=int)

        self.parser = parser

    def get_args(self) -> argparse.ArgumentParser:
        return self.parser.parse_args()


args = Args().get_args()
args.device = "cuda" if args.use_cuda else "cpu"


def main():
    try:
        print("> Starting the program")

        # Dataset
        dataset = WikipediaCorpus(args.dataset)

        # Model
        model = Word2Vec(dataset.embed_size, args.embedding_size)

        if args.n_gpu > 1:
            model = DataParallel(model)
        model.to(args.device)

        dl = DataLoader(
            dataset,
            drop_last=False,
            collate_fn=dataset.collate_fn,
            batch_size=args.batch_size,
            num_workers=0,
        )

        optimizer = optim.SparseAdam(model.parameters(), lr=args.learning_rate)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, len(dl))

        global_step = 0
        epochs_trained = 0

        # Loss
        train_loss = 0.0

        model.zero_grad()

        # Iterator
        train_iterator = trange(epochs_trained, args.num_train_epochs, desc="Epoch")

        for _ in train_iterator:
            epoch_iterator = tqdm(dl, desc="Steps")
            for _, batch in enumerate(epoch_iterator):
                model.train()
                word_pos, ctx, neg = batch
                word_pos = word_pos.to(args.device)
                ctx = ctx.to(args.device)
                neg = neg.to(args.device)
                loss = model(word_pos, ctx, neg)

                step_loss = loss.item() / len(word_pos)
                train_loss += step_loss

                loss.backward()

                optimizer.step()
                scheduler.step()
                model.zero_grad()

                global_step += 1

                if global_step % args.log_loss == 0:
                    print(f"Loss at step {global_step} --> {train_loss/global_step}")

            model.save(args.output_dir, "word_embedding")
            print(train_loss / global_step)
            epoch_iterator.close()

        print(">>> End of Training <<<")

    except KeyboardInterrupt:
        model.save(args.output_dir, "word_embedding")
        print("\n > Shutdown")


if __name__ == "__main__":
    main()