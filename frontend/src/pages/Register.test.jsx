import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Register from "./Register";

const register = vi.fn();
vi.mock("../context/AuthContext", () => ({ useAuth: () => ({ register }) }));

describe("Register", () => {
  it("blocks submission when passwords do not match", async () => {
    render(<MemoryRouter><Register /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText("First name"), { target: { value: "Noble" } });
    fireEvent.change(screen.getByLabelText("Last name"), { target: { value: "Ekwere" } });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "noble@example.com" } });
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: "noble" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "password123" } });
    fireEvent.change(screen.getByLabelText("Confirm password"), { target: { value: "different123" } });
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Passwords do not match.");
    expect(register).not.toHaveBeenCalled();
  });
});
