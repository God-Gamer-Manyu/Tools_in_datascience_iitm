import { html as la } from "https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";
import seedrandom from "https://cdn.jsdelivr.net/npm/seedrandom/+esm";
import { diffWords as diffWords } from "https://cdn.jsdelivr.net/npm/diff@7/+esm";

/*
    De-minified / reformatted version of the provided snippet.
    Assumes `ne` and `ke` are available in the same scope as before.
*/
export default async function ga({ user, weight = 1 }) {
    const id = "q-transcribe-tech-talk";
    const title = "Transcribe a reliability tech talk";

    // seeded RNG based on user email and id
    const rng = seedrandom(`${"24f3001383@ds.study.iitm.ac.in"}#${id}`);

    // choose length S and a random start index x within `ne`
    const S = Math.floor(rng() * 35) + 18;
    const x = Math.floor(rng() * (ne.length - S - 1));
    const k = x + S;

    // question / answer pieces from `ne`
    const question = ne[x][0];
    const endPiece = ne[k][1];
    const transcript = ne.slice(x, k + 1).map(([, , text]) => text).join("\n");

    // validator that checks differences between canonical transcript and submitted text
    const validate = async (submittedText) => {
        const diffCount = diffWords(ke(transcript), submittedText, { ignoreCase: true })
            .filter(({ added, removed }) => added || removed)
            .reduce((sum, part) => sum + (part.count || 0), 0);

        const maxAllowed = Math.ceil(S / 4);
        if (diffCount > maxAllowed) {
            throw new Error(`Detected ${diffCount} differences; expected at most ${maxAllowed}.`);
        }
        return true;
    };

    // return object shape matched to original: id, title, weight, question, answer (validator)
    return {
        id,
        title,
        weight,
        question,
        answer: validate
    };
}