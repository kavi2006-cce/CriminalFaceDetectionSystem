package com.project.criminalfacedetection.controller;

import com.project.criminalfacedetection.model.Criminal;
import com.project.criminalfacedetection.repository.CriminalRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/criminal")
@CrossOrigin("*")
public class CriminalController {

    private final CriminalRepository repo;

    public CriminalController(CriminalRepository repo) {
        this.repo = repo;
    }

    @PostMapping("/add")
    public Criminal addCriminal(@RequestBody Criminal criminal) {
        return repo.save(criminal);
    }

    @GetMapping("/all")
    public List<Criminal> getAll() {
        return repo.findAll();
    }

    @GetMapping("/{id}")
    public Criminal getCriminalById(@PathVariable Long id) {
        return repo.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Criminal not found with id: " + id));
    }

    @PutMapping("/{id}")
    public Criminal updateCriminal(@PathVariable Long id, @RequestBody Criminal updated)
    {
        return repo.findById(id)
                .map(criminal -> {
                    criminal.setName(updated.getName());
                    criminal.setAge(updated.getAge());
                    criminal.setGender(updated.getGender());
                    criminal.setCrimeType(updated.getCrimeType());
                    criminal.setLocation(updated.getLocation());
                    criminal.setPhoto(updated.getPhoto());
                    return repo.save(criminal);
                })
                .orElseThrow(() -> new IllegalArgumentException("Criminal not found with id: " + id));
    }

    @DeleteMapping("/{id}")
    public String deleteCriminal(@PathVariable Long id) {
        if (!repo.existsById(id)) {
            throw new IllegalArgumentException("Criminal not found with id: " + id);
        }
        repo.deleteById(id);
        return "Criminal deleted with id: " + id;
    }

    @GetMapping("/search")
    public List<Criminal> searchCriminals(@RequestParam(required = false, defaultValue = "") String name) {
        if (name.trim().isEmpty()) {
            return repo.findAll();
        }
        return repo.findAll().stream()
                .filter(c -> c.getName() != null && c.getName().toLowerCase().contains(name.toLowerCase()))
                .toList();
    }
}